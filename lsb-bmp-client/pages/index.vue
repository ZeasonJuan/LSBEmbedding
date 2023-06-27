<template>
  <cli-layout>
    <div style="display: flex; justify-content: center">
      <el-card style="min-width: 900px; width: 80%">
        <el-tabs v-model="activeName" type="card">
          <el-tab-pane label="嵌入信息" name="1">
            <lsb-do-card type="embed"/>
          </el-tab-pane>
          <el-tab-pane label="提取信息" name="2">
            <lsb-do-card type="extract"/>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </cli-layout>
</template>

<script>
import CliLayout from "~/components/base/CliLayout";

export default {
  name: 'IndexPage',
  components: {CliLayout},
  data() {
    return {
      activeName: '1',
    }
  },
}
</script>
