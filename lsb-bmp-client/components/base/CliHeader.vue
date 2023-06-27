<template>
  <div class="header_outer_box">
    <img class="header_logo"
         :src="require('~/static/img/bjtu.png')"
         alt="logo"
         height="50"/>

    <el-menu :default-active="activeIndex"
             class="el-menu-demo"
             style="height: 67px"
             mode="horizontal"
             @select="handleSelect">
      <slot v-for="item in navIndexList">
        <el-menu-item v-if="item.length === 1"
                      :index="item[0].index">
          {{ item[0].name }}
        </el-menu-item>
        <el-submenu v-else
                    :index="item[0].index">
          <template slot="title">
            {{ item[0].name }}
          </template>
          <el-menu-item v-for="(subItem, index) in item"
                        v-if="index !== 0"
                        :key="index"
                        :index="subItem.index">
            {{ subItem.name }}
          </el-menu-item>
        </el-submenu>
      </slot>
    </el-menu>

    <div/>
    <div v-if="activeIndex === '3'"
         style="position: absolute; display: flex; justify-content: right; flex-direction: column; right: 15px">
      <el-button type="primary" icon="el-icon-s-operation"
                 @click="$emit('openSearchDrawer')"></el-button>
    </div>
    <div v-else style="position: absolute; display: flex; justify-content: right; flex-direction: column; right: 15px">
      <div class="titleFont">
        <i class="el-icon-s-grid el-icon--left"/>当前页面
      </div>
      <div class="titleFont">
        {{ getCurPageName() }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "CliHeader",
  props: {
    curIndex: {
      type: String,
      default: "1"
    }
  },
  data() {
    return {
      activeIndex: '',
      navIndexList: [
        [
          {
            "index": "1",
            "name": "LSB信息隐藏",
            "path": "/"
          }
        ],
      ],
    };
  },
  mounted() {
    this.activeIndex = this.curIndex;
  },
  methods: {
    handleSelect(key, keyPath) {
      console.log(key, keyPath);
      this.navIndexList.forEach(outerNavItems => {
        outerNavItems.forEach(innerNavItem => {
          if (innerNavItem.index === key) {
            if (innerNavItem.path) {
              this.$router.push(innerNavItem.path);
            }
          }
        })
      });
    },

    getCurPageName() {
      let curPageName = "";
      for (let i = 0; i < this.navIndexList.length; i++) {
        let item = this.navIndexList[i];
        if (item.length === 1) {
          if (item[0].index === this.curIndex) {
            curPageName = item[0].name;
            break;
          }
        } else {
          for (let j = 1; j < item.length; j++) {
            if (item[j].index === this.curIndex) {
              curPageName = item[0].name + '-' + item[j].name;
              break;
            }
          }
        }
      }
      return curPageName;
    },
  }
}
</script>

<style scoped>
.header_outer_box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 68px;
}

.header_logo {
  margin-left: 15px;
}

.el-menu--horizontal > .el-menu-item {
  height: 68px;
}

.el-menu--horizontal > .el-submenu .el-submenu__title {
  height: 68px;
}

.titleFont {
  font-weight: bold;
  font-size: 16px;
  font-family: Microsoft YaHei;
  color: #2a5ad7;
  text-align: right;
}
</style>
