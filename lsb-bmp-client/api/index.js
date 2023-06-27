import axios from 'axios'
import PRO from './API_PRO.js'

let APICONFIG = PRO
let API = {}

for (var api in APICONFIG) {
  API[api] = (function (api) {
    return function (data, context) {
      return new Promise((resolve, reject) => {
        let apiInfo = APICONFIG[api]
        let method = apiInfo.method || APICONFIG.method

        let token = data ? data.token : undefined;
        let queryData = {};

        if (method === 'get' || method === 'delete') {
          // if method is get, send data as query parameters
          queryData = data ? JSON.parse(JSON.stringify(data)) : {};
          delete queryData.token;
        } else {
          // for other methods, send data in request body
          queryData = {};
          data.token && (queryData.token = data.token);
        }

        let config = {
          baseURL: APICONFIG.baseURL,
          url: apiInfo.url,
          method: apiInfo.method || method,
          params: queryData,
          data: method === 'get'|| method === 'delete' ? {} : data,
          headers: {
            token: token      // 理论上这里适配了JWT的token 有问题改这里
          }
        }

        axios(config).then((res) => {
          try {
            let apiData = res.data

            if (apiData.code !== 0) {
              if (context) {
                context.error({statusCode: 500, message: `CODE[${apiData.code}] ERROR[${apiData.message}]`})
                resolve({})
              } else {
                resolve(apiData)
              }
            } else if (apiData.code === 0 && apiData.data === null){
              resolve(apiData)
            } else {
              resolve(apiData.data)
            }
          } catch (err) {
          }
        }).catch(err => {
          if (err.response && err.response.status >= 500) {
            reject(err)
          } else if (err.response && err.response.status === 401) {
            resolve(err.response)
          } else {
            resolve(err.response.data)
          }
        })
      })
    }
  })(api)
}

API.CONFIG = APICONFIG

export default API
