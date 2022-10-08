import axios from "axios";
import cookie from "react-cookies";

const URL = "/api/v1/";

export default class API {
  constructor(entity) {
    this.url = `${URL}${entity}/`;
    axios.defaults.headers.common["X-CSRFTOKEN"] = cookie.load("csrftoken");
    axios.defaults.headers.common["Authorization"] = `Bearer ${window.localStorage.getItem('accessToken')}`;
    axios.interceptors.response.use(
      response => response,
      error => {
        const originalRequest = error.config;

        if (error.response.status === 401) {
          const refreshToken = window.localStorage.getItem('refreshToken');

          return axios
            .post(URL + 'token/refresh/', { refresh: refreshToken })
            .then(({ data }) => {
              window.localStorage.setItem('accessToken', data.access);

              axios.defaults.headers.common["Authorization"] = `Bearer ${data.access}`;
              originalRequest.headers["Authorization"] = `Bearer ${data.access}`;

              return axios(originalRequest);
            })
            .catch(err => {
              window.localStorage.removeItem('accessToken');
              window.localStorage.removeItem('refreshToken');
            });
        }

        return Promise.reject(error);
      }
    );
  }

  getAll = (query = {}) => {
    return axios.get(this.url, Object.assign({ params: { ...query } }));
  };
  getOne = id => {
    return axios.get(`${this.url}${id}/`);
  };
  create = toCreate => {
    return axios.post(this.url, toCreate);
  };
  update = toUpdate => {
    return axios.put(`${this.url}${toUpdate.id}/`, toUpdate);
  };
  patch = (id, toPatch) => {
    return axios.patch(`${this.url}${id}/`, toPatch);
  };
  delete = id => {
    return axios.delete(`${this.url}${id}/`);
  };
}

