# Vue integration example

This example follows the mixed-auth API design from the planning notes:

- public pages fetch `/public/`
- authenticated pages fetch `/all-enabled/`

## Public page example

```vue
<script setup>
import { onMounted, ref } from "vue"

const publicFlags = ref({})

onMounted(async () => {
  const response = await fetch("/api/feature-flags/public/")
  publicFlags.value = await response.json()
})
</script>

<template>
  <section v-if="publicFlags.new-pricing-model">
    <h2>New pricing is rolling out</h2>
  </section>
</template>
```

## Authenticated app example

```vue
<script setup>
import { computed, onMounted, ref } from "vue"

const flags = ref({})

const isEnabled = (name) => Boolean(flags.value[name])

const fetchFlags = async (context = null) => {
  const params = new URLSearchParams()

  if (context) {
    params.set("context_app_label", context.appLabel)
    params.set("context_model", context.model)
    params.set("context_id", String(context.id))
  }

  const url = params.size
    ? `/api/feature-flags/all-enabled/?${params.toString()}`
    : "/api/feature-flags/all-enabled/"

  const response = await fetch(url, {
    credentials: "include",
  })
  flags.value = await response.json()
}

onMounted(() => {
  fetchFlags()
})
</script>

<template>
  <button v-if="isEnabled('bulk-trip-import')">Import Trips</button>
</template>
```

## Optional composable

```javascript
import { computed, ref } from "vue"

export const useFeatureFlags = () => {
  const flags = ref({})

  const isEnabled = (name) => Boolean(flags.value[name])

  const fetchFlags = async (endpoint = "/api/feature-flags/all-enabled/") => {
    const response = await fetch(endpoint, {
      credentials: "include",
    })
    flags.value = await response.json()
  }

  return {
    flags: computed(() => flags.value),
    isEnabled,
    fetchFlags,
  }
}
```
