<template>
  <div>
    <div style="display: flex">
      <div style="display: flex; flex-direction: column; margin-left: 10px; align-items: center; padding-bottom: 23px">
        <div class="step-title">① 上传你的图片</div>
        <el-upload :action="'http://localhost:5000/editor/upload' + '?type=' + type"
                   accept=".bmp"
                   :limit="1"
                   drag
                   :on-change="handleLimit"
                   :class="{disabled: uploadDisabled}"
                   list-type="picture-card"
                   :on-success="handleSuccess"
                   :on-remove="handleRemove">
          <i class="el-icon-plus"/>
        </el-upload>
      </div>

      <div v-loading="loading"
           style="display: flex; flex-direction: column; align-items: center; margin-left: 20px; flex: 1">
        <div class="step-title">
          ② {{ type === 'embed' ? '确认嵌入信息' : '提取嵌入信息' }}
        </div>
        <div v-if="type === 'embed'" style="font-size: 18px; margin-bottom: 15px;">
          <div style="font-weight: bold; color: #2a5ad7; display: inline">可嵌入信息长度：</div>
          {{ embedInfoLen !== '' ? embedInfoLen : '上传嵌入图片后处理' }}
          <el-tooltip class="item" effect="dark" :content="embedInfoLenConvert" placement="top">
            <i class="el-icon-info"></i>
            <div slot="content" class="tooltip-content">
              <div v-html="embedInfoLenConvert">
                {{embedInfoLenConvert}}
              </div>
            </div>
          </el-tooltip>
        </div>
        <el-input
          type="textarea"
          :rows="type === 'embed' ? 4 : 8"
          :placeholder="type === 'embed' ? '请输入内容' : '等待上传图片'"
          v-model="textarea">
        </el-input>
        <el-button v-if="type === 'embed'"
                   type="primary"
                   style="margin-top: 15px;"
                   @click="submitLsbTask">
          嵌入信息
        </el-button>
      </div>

      <div v-if="type === 'embed'"
           style="display: flex; flex-direction: column; align-items: center; margin-left: 20px; margin-right: 10px; position: relative;">
        <div class="step-title">③ 嵌入后的图片</div>
        <el-empty v-if="!lsbFin" description="等待处理"></el-empty>
        <el-image v-else
                  :src="finPicSrc"
                  style="width: 180px; height: 180px"
                  fit="contain">
          <div slot="placeholder" class="image-slot">
            等待处理<span class="dot">...</span>
          </div>
        </el-image>
        <el-button v-if="lsbFin"
                   type="primary"
                   style="position: absolute; bottom: 0; right: 0"
                   icon="el-icon-download"
                   @click="downloadFinPic"
                   circle />
      </div>
    </div>
  </div>
</template>

<script>
import API from "~/api";

export default {
  name: "LsbDoCard",
  props: {
    type: {
      type: String,
      default: 'embed',
    },
  },
  data() {
    return {
      finPicSrc: '',
      lsbFin: false,
      loading: false,
      uploadDisabled: false,
      embedInfoLen: '',
      embedInfoLenConvert: '上传嵌入图片后处理',
      textarea: '',
      procPicFilename: '',
    }
  },
  methods: {
    downloadFinPic() {
      let url = this.finPicSrc;
      let fileName = this.procPicFilename;
      fileName = fileName.substring(0, fileName.lastIndexOf('.')) + '_lsb_embed' + fileName.substring(fileName.lastIndexOf('.'));

      let xhr = new XMLHttpRequest();
      xhr.open('GET', url, true);
      xhr.responseType = 'blob';

      xhr.onload = function() {
        if (xhr.status === 200) {
          let blob = xhr.response;
          let a = document.createElement('a');
          a.href = window.URL.createObjectURL(blob);
          a.download = fileName;
          a.style.display = 'none';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(a.href);
        }
      };

      xhr.send();
    },

    submitLsbTask() {
      this.loading = true;
      this.$message.info('信息处理中');

      let data = {
        filename: this.procPicFilename,
        info: this.textarea,
      }

      API.submitLsb(data).then(res => {
        console.log(res)
        if (res.code) {
          this.$message.error(res.msg);
          this.loading = false;
          return;
        }

        this.$message.success("嵌入信息成功");
        this.finPicSrc = res.url;
        this.lsbFin = true;
        this.loading = false;
      }).catch(err => {
        this.$message.error("嵌入信息失败");
        console.log(err);
      });
    },

    handleLimit(file, fileList) {
      this.uploadDisabled = fileList.length >= 1;
      this.$forceUpdate();
    },

    handleSuccess(response, file, fileList) {
      if (response.code !== 0) {
        this.$message.error(response.msg);
        return;
      }

      if (this.type === 'embed') {
        this.$message.success("图片上传成功，请完成下一步操作");
        this.embedInfoLen = response.data.main_max_lsb_length;
        this.embedInfoLenConvert = response.data.sub_max_lsb_length.replace(/\n/g, '<br/>');
        this.procPicFilename = response.data.filename;
      } else {
        this.$message.success("LSB隐写信息提取成功");
        this.textarea = response.data.info;
      }
    },

    handleRemove(file, fileList) {
      console.log(file, fileList);
      this.uploadDisabled = false;
      this.$forceUpdate();
    },
  },
}
</script>

<style scoped>
.step-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #2a5ad7;
}

.disabled {
  width: 180px;
  height: 180px;
}

>>> .disabled .el-upload.el-upload--picture-card {
  display: none !important;
}

>>> .disabled .el-button--success.is-plain {
  display: none !important;
}

>>> .el-empty {
  padding: 0;
}

>>> .el-upload-dragger {
  width: 180px;
  height: 180px;
}

>>> .el-upload--picture-card {
  width: 180px;
  height: 180px;
  line-height: 180px;
}

>>> .el-empty__description {
  margin-top: 10px;
}

>>> .el-upload-list--picture-card .el-upload-list__item-thumbnail {
  object-fit: contain;
}

>>> .el-upload-list--picture-card .el-upload-list__item {
  width: 180px;
  height: 180px;
}
</style>
