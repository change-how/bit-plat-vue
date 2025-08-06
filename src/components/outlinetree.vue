<template>
  <el-tree
    style="max-width: 600px"
    :data="data"
    :props="defaultProps"
    @node-click="handleNodeClick"
  />
</template>

<script lang="ts" setup>
interface Tree {
  label: string
  children?: Tree[]
}

const handleNodeClick = (data: Tree) => {
  console.log(data)
}

const data: Tree[] = [
  {
    label: 'Level one 1',
    children: [
      {
        label: 'Level two 1-1',
        children: [
          {
            label: 'Level three 1-1-1',
          },
        ],
      },
    ],
  },
  {
    label: 'Level one 2',
    children: [
      {
        label: 'Level two 2-1',
        children: [
          {
            label: 'Level three 2-1-1',
          },
        ],
      },
      {
        label: 'Level two 2-2',
        children: [
          {
            label: 'Level three 2-2-1',
          },
        ],
      },
    ],
  },
  {
    label: 'Level one 3',
    children: [
      {
        label: 'Level two 3-1',
        children: [
          {
            label: 'Level three 3-1-1',
          },
        ],
      },
      {
        label: 'Level two 3-2',
        children: [
          {
            label: 'Level three 3-2-1',
          },
        ],
      },
    ],
  },
]

const defaultProps = {
  children: 'children',
  label: 'label',
}
</script>

<style scoped>
/* 使用 :deep() 选择器来穿透 scoped 限制，修改子组件样式 */

/* 整体背景和字体颜色 */
:deep(.el-tree) {
  background-color: #ffffff; /* 白色背景 */
  color: #3c4043; /* 深灰色字体 */
  font-family: 'Google Sans', sans-serif, Arial; /* 优先使用 Google Sans 字体 */
  font-size: 20px; /* --- 新增：调整基础字体大小 --- */
}

/* 树节点内容区域的样式 */
:deep(.el-tree-node__content) {
  border-radius: 4px; /* 添加圆角 */
  margin: 2px 0;
  transition: background-color 0.2s ease; /* 平滑的背景色过渡 */
  height: 32px; /* --- 修改：调整节点高度以适应新字号 --- */
  
}

/* 鼠标悬停在节点上时的样式 */
:deep(.el-tree-node__content:hover) {
  background-color: #f1f3f4; /* 淡灰色背景 */
}

/* 节点被选中时的样式 */
:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background-color: #e8f0fe; /* 淡蓝色背景 */
  color: #1967d2; /* 蓝色字体 */
}

/* 节点获得焦点时的外框样式（为了可访问性） */
:deep(.el-tree-node:focus > .el-tree-node__content) {
  background-color: #e8f0fe; /* 同选中样式 */
  outline: none; /* 移除默认 outline */
}

/* 修改展开/折叠图标的颜色 */
:deep(.el-tree-node__expand-icon) {
  color: #5f6368;
}
:deep(.el-tree-node__expand-icon.is-leaf) {
  color: transparent; /* 叶子节点前不显示图标 */
}

/* 选中节点时，图标颜色也改变 */
:deep(.el-tree-node.is-current > .el-tree-node__content .el-tree-node__expand-icon) {
    color: #1967d2;
}

</style>