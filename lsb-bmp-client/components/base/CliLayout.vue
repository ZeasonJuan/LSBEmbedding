<template>
  <div class="outStyle">
    <div class="titleStyle">
      <cli-header @openSearchDrawer="$emit('openSearchDrawer')" :cur-index="curIndex"></cli-header>
    </div>
    <div id="water_marker_body" class="bodyStyle" ref="scrollBody">
      <div class="innerStyle">
        <div style="width: 100%; height: 100%;">
          <!--          <el-card class="innerBodyStyle">-->
          <!--            <slot></slot>-->
          <!--          </el-card>-->
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CliHeader from "~/components/base/CliHeader";

export default {
  name: "CliLayout",
  props: {
    curIndex: {
      type: String,
    }
  },
  components: {CliHeader},
}
</script>

<style scoped>
html, body {
  margin: 0;
  padding: 0;
  height: calc(100% + 8px);
}

.outStyle {
  position: absolute;
  top: 0;
  left: 0;
}

.titleStyle {
  position: fixed;
  width: 100%;
  height: auto;
  z-index: 1000;
  transition: 1s;
}

.bodyStyle {
  position: fixed;
  top: 68px;
  width: 100%;
  max-width: 2000px;
  min-height: calc(100vh - 68px);
  height: calc(100vh - 68px);
  min-width: 100%;
  overflow: auto;
  background-color: #E4ECF5;

  animation: upShow 0.5s;
  -moz-animation: upShow 0.5s; /* Firefox */
  -webkit-animation: upShow 0.5s; /* Safari 和 Chrome */
  -o-animation: upShow 0.5s; /* Opera */
}

.bodyStyle::-webkit-scrollbar {
  width: 0 !important;
}

.bodyStyle::-webkit-scrollbar-thumb {
  height: 5px;
  background: #2a5ad7;
  border-radius: 5px;
}

.innerStyle {
  padding: 1.5rem 1.5rem 3.2rem;
  min-height: 100vh;
  display: flex;
  justify-content: center;
}

.innerStyle2 {
  padding: 1.5rem 1.5rem 3.2rem;
  min-height: 100vh;
  width: max(1920px, 100%);
}

@-webkit-keyframes upShow {
  from {
    opacity: 0;
    -webkit-transform: translate(0, 80px); /* Safari */
    transform: translate(0, 80px); /* 标准语法 */
  }
  to {
    opacity: 1;
    -webkit-transform: translate(0, 0px); /* Safari */
    transform: translate(0, 0px); /* 标准语法 */
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
  transition-delay: 1s;
}

.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */
{

  transition-delay: 0s;
  opacity: 0;
}

.innerBodyStyle {
  position: absolute;
  left: 3%;
  right: 3%;
  top: 5%;
  min-height: 90%;
  height: fit-content;
  padding: 1px;
}
</style>
