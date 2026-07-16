from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandError

from feature_flags.models import FeatureFlag


class Command(BaseCommand):
    help = "Create, list, and update feature flags."

    def add_arguments(self, parser: Any) -> None:
        subparsers = parser.add_subparsers(dest="action", required=True)

        subparsers.add_parser("list", help="List existing feature flags.")

        create_parser = subparsers.add_parser("create", help="Create a feature flag.")
        create_parser.add_argument("name")
        create_parser.add_argument("--description", default="")
        create_parser.add_argument("--public", action="store_true")
        create_parser.add_argument("--disabled", action="store_true")

        toggle_parser = subparsers.add_parser("toggle", help="Flip a feature flag on or off.")
        toggle_parser.add_argument("name")

        set_parser = subparsers.add_parser("set", help="Set the state of a feature flag.")
        set_parser.add_argument("name")
        state_group = set_parser.add_mutually_exclusive_group(required=True)
        state_group.add_argument("--enabled", action="store_true")
        state_group.add_argument("--disabled", action="store_true")
        public_group = set_parser.add_mutually_exclusive_group()
        public_group.add_argument("--public", action="store_true")
        public_group.add_argument("--private", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        action = options["action"]

        if action == "list":
            self.handle_list()
            return

        if action == "create":
            self.handle_create(**options)
            return

        if action == "toggle":
            self.handle_toggle(options["name"])
            return

        if action == "set":
            self.handle_set(**options)
            return

        raise CommandError(f"Unsupported action: {action}")

    def handle_list(self) -> None:
        flags = FeatureFlag.objects.all()
        if not flags.exists():
            self.stdout.write("No feature flags found.")
            return

        for flag in flags:
            access = "public" if flag.is_public else "authenticated"
            status = "enabled" if flag.is_enabled else "disabled"
            self.stdout.write(f"{flag.name}: {status} ({access})")

    def handle_create(self, **options: Any) -> None:
        flag, created = FeatureFlag.objects.get_or_create(
            name=options["name"],
            defaults={
                "description": options["description"],
                "is_public": options["public"],
                "is_enabled": not options["disabled"],
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created feature flag '{flag.name}'."))
            return

        raise CommandError(f"Feature flag '{flag.name}' already exists.")

    def handle_toggle(self, name: str) -> None:
        flag = self.get_flag(name)
        flag.is_enabled = not flag.is_enabled
        flag.save(update_fields=["is_enabled", "updated_at"])
        state = "enabled" if flag.is_enabled else "disabled"
        self.stdout.write(self.style.SUCCESS(f"Feature flag '{flag.name}' is now {state}."))

    def handle_set(self, **options: Any) -> None:
        flag = self.get_flag(options["name"])
        flag.is_enabled = bool(options["enabled"])
        if options["public"]:
            flag.is_public = True
        elif options["private"]:
            flag.is_public = False

        flag.save(update_fields=["is_enabled", "is_public", "updated_at"])
        access = "public" if flag.is_public else "authenticated"
        state = "enabled" if flag.is_enabled else "disabled"
        self.stdout.write(
            self.style.SUCCESS(f"Feature flag '{flag.name}' set to {state} ({access}).")
        )

    def get_flag(self, name: str) -> FeatureFlag:
        try:
            return FeatureFlag.objects.get(name=name)
        except FeatureFlag.DoesNotExist as exc:
            raise CommandError(f"Feature flag '{name}' does not exist.") from exc
