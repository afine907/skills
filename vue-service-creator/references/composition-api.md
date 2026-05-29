# Composition API 模式与最佳实践

Vue 3 Composition API 的常用模式、设计原则和最佳实践参考。

## 响应式基础

### ref vs reactive 选择原则

```typescript
import { ref, reactive, shallowRef, shallowReactive, toRef, toRefs } from 'vue';

// ref — 推荐用于：
// 1. 基本类型 (string, number, boolean)
// 2. 需要整体替换的对象
const count = ref(0);
const user = ref<User | null>(null);

// reactive — 推荐用于：
// 1. 表单对象（字段多，逐个 ref 太繁琐）
// 2. 不需要整体替换的复杂对象
const form = reactive({
  username: '',
  password: '',
  remember: false,
});

// shallowRef / shallowReactive — 性能优化
// 仅顶层属性响应式，适用于大型只读数据
const largeList = shallowRef<Data[]>([]);
const config = shallowReactive({ theme: 'light', locale: 'zh-CN' });

// toRef / toRefs — 解构保持响应性
const { username, password } = toRefs(form);
const singleField = toRef(form, 'username');
```

### 响应式丢失与恢复

```typescript
import { ref, toRef, toRefs, computed } from 'vue';

// 问题：直接解构 reactive 会丢失响应性
const state = reactive({ count: 0, name: 'test' });
const { count, name } = state;  // count 和 name 不再响应式

// 解决方案 1：toRefs
const { count, name } = toRefs(state);

// 解决方案 2：toRef 单个属性
const count = toRef(state, 'count');

// 解决方案 3：computed 包装
const count = computed(() => state.count);

// 问题：ref 对象被 reactive 包裹后自动解包
const countRef = ref(0);
const state = reactive({ count: countRef }); // state.count 自动解包为 number
// 访问 state.count 不需要 .value
```

## Composables 设计模式

### 基础 composable 模板

```typescript
// composables/useCounter.ts
import { ref, computed } from 'vue';

export function useCounter(initialValue = 0) {
  const count = ref(initialValue);

  const doubled = computed(() => count.value * 2);

  function increment() { count.value++; }
  function decrement() { count.value--; }
  function reset() { count.value = initialValue; }

  return {
    count: readonly(count),    // 暴露只读版本，防止外部修改
    doubled,
    increment,
    decrement,
    reset,
  };
}
```

### 异步数据 composable

```typescript
// composables/useAsyncData.ts
import { ref, watchEffect, type Ref } from 'vue';

interface UseAsyncDataOptions<T> {
  immediate?: boolean;
  defaultValue?: T;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

export function useAsyncData<T>(
  fetcher: () => Promise<T>,
  options: UseAsyncDataOptions<T> = {}
) {
  const data = ref<T | undefined>(options.defaultValue) as Ref<T | undefined>;
  const pending = ref(false);
  const error = ref<Error | null>(null);

  async function execute() {
    pending.value = true;
    error.value = null;
    try {
      data.value = await fetcher();
      options.onSuccess?.(data.value as T);
    } catch (err) {
      error.value = err as Error;
      options.onError?.(err as Error);
    } finally {
      pending.value = false;
    }
  }

  if (options.immediate !== false) {
    execute();
  }

  return { data, pending, error, refresh: execute };
}
```

### 事件监听 composable

```typescript
// composables/useEventListener.ts
import { onMounted, onUnmounted, watch, type Ref } from 'vue';

export function useEventListener(
  target: Ref<EventTarget | null> | EventTarget,
  event: string,
  handler: (e: Event) => void
) {
  if (typeof target === 'object' && 'value' in target) {
    watch(target, (el, oldEl) => {
      oldEl?.removeEventListener(event, handler);
      el?.addEventListener(event, handler);
    }, { immediate: true });
  } else {
    onMounted(() => target.addEventListener(event, handler));
    onUnmounted(() => target.removeEventListener(event, handler));
  }
}
```

### localStorage 同步 composable

```typescript
// composables/useStorage.ts
import { ref, watch } from 'vue';

export function useStorage<T>(key: string, defaultValue: T) {
  const stored = localStorage.getItem(key);
  const data = ref<T>(stored ? JSON.parse(stored) : defaultValue);

  watch(data, (val) => {
    localStorage.setItem(key, JSON.stringify(val));
  }, { deep: true });

  return data;
}
```

## 组件设计模式

### 受控组件模式

```vue
<!-- components/ui/BaseInput.vue -->
<script setup lang="ts">
interface Props {
  modelValue: string;
  label?: string;
  error?: string;
  placeholder?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
});

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" class="text-sm font-medium text-gray-700">
      {{ label }}
    </label>
    <input
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="[
        'rounded-md border px-3 py-2 text-sm transition-colors',
        error ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-blue-500',
        disabled && 'cursor-not-allowed opacity-50',
      ]"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
  </div>
</template>
```

### 动态组件与 keep-alive

```vue
<script setup lang="ts">
import { shallowRef } from 'vue';
import TabHome from './tabs/TabHome.vue';
import TabSettings from './tabs/TabSettings.vue';

const tabs = { TabHome, TabSettings };
const currentTab = shallowRef(TabHome);
</script>

<template>
  <KeepAlive>
    <component :is="currentTab" />
  </KeepAlive>
</template>
```

### 模板引用

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';

const inputRef = ref<HTMLInputElement | null>(null);

onMounted(() => {
  inputRef.value?.focus();
});

// 暴露给父组件
defineExpose({
  focus: () => inputRef.value?.focus(),
});
</script>

<template>
  <input ref="inputRef" type="text" />
</template>
```

## 性能优化

### v-once / v-memo

```vue
<template>
  <!-- 静态内容，只渲染一次 -->
  <header v-once>
    <h1>{{ title }}</h1>
    <p>{{ subtitle }}</p>
  </header>

  <!-- 条件缓存，仅依赖变化时重新渲染 -->
  <div v-for="item in list" :key="item.id" v-memo="[item.selected]">
    <p>{{ item.name }}</p>
    <input type="checkbox" :checked="item.selected" />
  </div>
</template>
```

### 懒加载组件

```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue';

const HeavyChart = defineAsyncComponent(() =>
  import('./components/HeavyChart.vue')
);
// 带 loading/error 状态
const HeavyEditor = defineAsyncComponent({
  loader: () => import('./components/HeavyEditor.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200,
  errorComponent: ErrorDisplay,
  timeout: 10000,
});
</script>
```

### computed 缓存注意事项

```typescript
import { computed } from 'vue';

// 好：纯函数依赖，自动缓存
const sortedList = computed(() => {
  return [...list.value].sort((a, b) => a.name.localeCompare(b.name));
});

// 坏：computed 中产生副作用
const result = computed(() => {
  sideEffect(); // 不要在 computed 中产生副作用
  return data.value;
});

// 坏：computed 中发起异步请求（应使用 watch 或 watchEffect）
const user = computed(async () => {
  return await fetchUser(id.value); // 不推荐
});
```

## TypeScript 类型技巧

### 组件 Props 类型

```typescript
// 方式 1：类型别名
interface Props {
  title: string;
  count?: number;
  items: string[];
  onSelect: (id: string) => void;
}
const props = defineProps<Props>();

// 方式 2：带默认值（使用 withDefaults）
const props = withDefaults(defineProps<Props>(), {
  count: 0,
  items: () => [],
});
```

### 事件类型

```typescript
// 内联事件类型
const emit = defineEmits<{
  change: [id: string, value: number];
  delete: [id: string];
}>();

// 事件类型别名
type Emits = {
  change: [id: string, value: number];
  delete: [id: string];
};
const emit = defineEmits<Emits>();
```

### 模板引用类型

```typescript
const inputRef = ref<InstanceType<typeof BaseInput> | null>(null);

// 使用 DOM 元素类型
const canvasRef = ref<HTMLCanvasElement | null>(null);
```
