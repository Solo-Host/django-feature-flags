# TypeScript integration example

This example shows a **generic** TypeScript integration that works for any flag
name and any optional scoped context.

Use the frontend API for **UX gates** and keep `is_feature_enabled(...)` on the
backend for **enforcement** of mutating operations.

## Typed API helpers

```ts
export interface FeatureFlagContext {
  appLabel: string
  model: string
  id: string | number
}

export type EnabledFeatureFlagMap = Record<string, true>

export interface FeatureFlagMetadata {
  name: string
  description: string
  is_enabled: boolean
  is_public: boolean
  enabled: boolean
  has_user_restrictions: boolean
  has_context_restrictions: boolean
  created_at: string
  updated_at: string
}

function buildFeatureFlagQuery(context?: FeatureFlagContext): URLSearchParams {
  const params = new URLSearchParams()

  if (!context) {
    return params
  }

  params.set("context_app_label", context.appLabel)
  params.set("context_model", context.model)
  params.set("context_id", String(context.id))
  return params
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url, {
    credentials: "include",
  })

  if (!response.ok) {
    throw new Error(`Feature flag request failed: ${response.status}`)
  }

  return (await response.json()) as T
}

export async function fetchEnabledFeatureFlags(
  context?: FeatureFlagContext,
): Promise<EnabledFeatureFlagMap> {
  const params = buildFeatureFlagQuery(context)
  const suffix = params.size > 0 ? `?${params.toString()}` : ""

  return fetchJson<EnabledFeatureFlagMap>(`/api/feature-flags/all-enabled/${suffix}`)
}

export async function fetchFeatureFlagState(
  featureName: string,
  context?: FeatureFlagContext,
): Promise<boolean> {
  const params = buildFeatureFlagQuery(context)
  const suffix = params.size > 0 ? `?${params.toString()}` : ""
  const data = await fetchJson<{ enabled: boolean }>(
    `/api/feature-flags/${featureName}/is-enabled/${suffix}`,
  )

  return data.enabled
}

export async function fetchFeatureFlagDetails(
  featureName: string,
  context?: FeatureFlagContext,
): Promise<FeatureFlagMetadata> {
  const params = buildFeatureFlagQuery(context)
  const suffix = params.size > 0 ? `?${params.toString()}` : ""

  return fetchJson<FeatureFlagMetadata>(`/api/feature-flags/${featureName}/${suffix}`)
}

export function isFeatureEnabled(
  flags: EnabledFeatureFlagMap,
  featureName: string,
): boolean {
  return Boolean(flags[featureName])
}
```

## Optional Vue + Pinia store

```ts
import { defineStore } from "pinia"
import { ref } from "vue"

type EnabledFlagsByContext = Record<string, EnabledFeatureFlagMap>

function contextKey(context?: FeatureFlagContext): string {
  return context ? `${context.appLabel}:${context.model}:${String(context.id)}` : "global"
}

export const useFeatureFlagsStore = defineStore("featureFlags", () => {
  const enabledFlagsByContext = ref<EnabledFlagsByContext>({})

  function getEnabledFlags(context?: FeatureFlagContext): EnabledFeatureFlagMap {
    return enabledFlagsByContext.value[contextKey(context)] ?? {}
  }

  function isEnabled(name: string, context?: FeatureFlagContext): boolean {
    return Boolean(getEnabledFlags(context)[name])
  }

  async function loadEnabledFlags(context?: FeatureFlagContext): Promise<void> {
    enabledFlagsByContext.value = {
      ...enabledFlagsByContext.value,
      [contextKey(context)]: await fetchEnabledFeatureFlags(context),
    }
  }

  return {
    enabledFlagsByContext,
    getEnabledFlags,
    isEnabled,
    loadEnabledFlags,
  }
})
```

That gives you one generic flow for all flags:

- load enabled flags for the current context
- check `store.isEnabled("some-flag")`
- fetch `fetchFeatureFlagDetails("some-flag")` only when you need metadata

## Backend enforcement example

```python
from feature_flags.utils import is_feature_enabled


def import_records(request, workspace):
    if not is_feature_enabled("bulk-trip-import", user=request.user, context=workspace):
        raise PermissionDenied("Feature is disabled.")

    # continue with the write operation
```

## Cleanup checklist

When a flag is retired:

1. remove the frontend consumer (`isEnabled(...)`, store usage, hidden UI)
2. remove the backend enforcement check
3. remove any seeded/default flag data
4. remove the flag entry from your project-level feature-flag inventory
