from __future__ import annotations

from typing import Any, cast

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from feature_flags.models import FeatureFlag
from feature_flags.serializers import FeatureFlagSerializer
from feature_flags.utils import get_feature_flag_states


class FeatureFlagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FeatureFlagSerializer
    lookup_field = "name"

    def get_queryset(self) -> models.QuerySet[FeatureFlag]:
        return FeatureFlag.objects.prefetch_related("allowed_users", "targets")

    def get_permissions(self) -> list[Any]:
        permission_classes = [AllowAny] if self.action == "public" else [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_context(self) -> dict[str, Any]:
        context = dict(super().get_serializer_context())
        context["feature_flag_context"] = self.get_flag_context()
        return context

    def get_flag_context(self) -> models.Model | None:
        app_label = self.request.query_params.get("context_app_label")
        model_name = self.request.query_params.get("context_model")
        object_id = self.request.query_params.get("context_id")

        if app_label is None and model_name is None and object_id is None:
            return None

        if not all([app_label, model_name, object_id]):
            raise ValidationError(
                "context_app_label, context_model, and context_id must be supplied together."
            )

        if app_label is None or model_name is None or object_id is None:
            raise ValidationError(
                "context_app_label, context_model, and context_id must be supplied together."
            )

        try:
            model_class = cast(type[models.Model], apps.get_model(app_label, model_name))
        except LookupError as exc:
            raise ValidationError("Invalid feature flag context model.") from exc

        try:
            return model_class._default_manager.get(pk=object_id)
        except ObjectDoesNotExist as exc:
            raise NotFound("Requested feature flag context was not found.") from exc

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def public(self, request: Request) -> Response:
        context = self.get_flag_context()
        flags = self.get_queryset().filter(is_enabled=True, is_public=True)
        states = get_feature_flag_states(queryset=flags, context=context)
        return Response({name: True for name, enabled in states.items() if enabled})

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="all-enabled",
        url_name="all-enabled",
    )
    def all_enabled(self, request: Request) -> Response:
        context = self.get_flag_context()
        flags = self.get_queryset().filter(is_enabled=True)
        states = get_feature_flag_states(queryset=flags, user=request.user, context=context)
        return Response({name: True for name, enabled in states.items() if enabled})

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="is-enabled",
        url_name="is-enabled",
    )
    def is_enabled(self, request: Request, name: str | None = None) -> Response:
        context = self.get_flag_context()
        flag = self.get_object()
        return Response({"enabled": flag.is_enabled_for_user(user=request.user, context=context)})
