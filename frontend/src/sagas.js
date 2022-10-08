import { takeLatest, takeEvery, call, put, all } from "redux-saga/effects";
import API from './api';

export function* rootSaga() {
  yield all([
    takeLatest("DASHBOARD_READ_REQUEST", dashboardReadSaga),
    takeLatest("PROFILE_READ_REQUEST", profileReadSaga),
    takeLatest("PROFILE_UPDATE_REQUEST", profileUpdateSaga),
    takeLatest("PLANT_READ_REQUEST", plantReadSaga),
    takeLatest("PLANT_CREATE_REQUEST", plantCreateSaga),
    takeLatest("PLANT_DELETE_REQUEST", plantDeleteSaga),
    takeLatest("LOGIN_REQUEST", loginSaga),
    takeLatest("SENSOR_READ_REQUEST", sensorReadSaga),
    takeLatest("SENSOR_CREATE_REQUEST", sensorCreateSaga),
    takeLatest("SENSOR_DELETE_REQUEST", sensorDeleteSaga),
    takeLatest("ACTUATOR_READ_REQUEST", actuatorReadSaga),
    takeLatest("ACTUATOR_CREATE_REQUEST", actuatorCreateSaga),
    takeLatest("ACTUATOR_DELETE_REQUEST", actuatorDeleteSaga),
    takeEvery("TRENDS_READ_REQUEST", trendsReadSaga),
  ]);
}

function* dashboardReadSaga() {
  try {
    const dashboardAPI = new API("dashboard");
    const response = yield call(dashboardAPI.getAll);
    const structure = response.data[0].structure;
    yield put({ type: "DASHBOARD_READ_SUCCESS", structure });
  } catch (error) {
    yield put({ type: "DASHBOARD_READ_FAILURE", error });
  }
}
function* profileReadSaga() {
  try {
    const profileAPI = new API("profile");
    const response = yield call(profileAPI.getAll);
    const remoteToken = response.data[0].remoteToken;
    const id = response.data[0].id;
    yield put({ type: "PROFILE_READ_SUCCESS", remoteToken, id });
  } catch (error) {
    yield put({ type: "PROFILE_READ_FAILURE", error });
  }
}
function* profileUpdateSaga(action) {
  try {
    const profileAPI = new API("profile");
    const response = yield call(profileAPI.update, action.payload);
    const remoteToken = response.data[0].remoteToken;
    const id = response.data[0].id;
    yield put({ type: "PROFILE_UPDATE_SUCCESS", remoteToken, id });
  } catch (error) {
    yield put({ type: "PROFILE_UPDATE_FAILURE", error });
  }
}

function* plantReadSaga() {
  try {
    const plantsAPI = new API("plant");
    const response = yield call(plantsAPI.getAll);
    const plants = response.data;
    yield put({ type: "PLANT_READ_SUCCESS", plants });
  } catch (error) {
    yield put({ type: "PLANT_READ_FAILURE", error });
  }
}
function* plantCreateSaga(action) {
  try {
    const plantsAPI = new API("plant");
    const response = yield call(plantsAPI.create, action.payload);
    const plant = response.data;
    yield put({ type: "PLANT_CREATE_SUCCESS", plant });
  } catch (error) {
    yield put({ type: "PLANT_CREATE_FAILURE", error });
  }
}
function* plantDeleteSaga(action) {
  try {
    const plantsAPI = new API("plant");
    yield call(plantsAPI.delete, action.payload.id);
    yield put({ type: "PLANT_DELETE_SUCCESS" , id: action.payload.id });
  } catch (error) {
    yield put({ type: "PLANT_DELETE_FAILURE", error });
  }
}

function* loginSaga(action) {
  try {
    const loginAPI = new API("token");
    const response = yield call(loginAPI.create, action.payload);
    const accessToken = response.data.access;
    const refreshToken = response.data.refresh;
    yield put({ type: "LOGIN_SUCCESS", accessToken, refreshToken });
  } catch (error) {
    yield put({ type: "LOGIN_FAILURE", error });
  }
}
function* trendsReadSaga(action) {
  try {
    const trendsAPI = new API("snapshot");
    const response = yield call(trendsAPI.getAll, action.payload);
    const trends = response.data;
    const payload = action.payload;
    yield put({ type: "TRENDS_READ_SUCCESS", trends, payload });
  } catch (error) {
    yield put({ type: "TRENDS_READ_FAILURE", error });
  }
}

function* sensorReadSaga(action) {
  try {
    const sensorsAPI = new API("device");
    const response = yield call(sensorsAPI.getAll, action.payload);
    const sensors = response.data;
    yield put({ type: "SENSOR_READ_SUCCESS", sensors });
  } catch (error) {
    yield put({ type: "SENSOR_READ_FAILURE", error });
  }
}

function* sensorCreateSaga(action) {
  try {
    const sensorAPI = new API("device");
    const response = yield call(sensorAPI.create, action.payload);
    const sensor = response.data;
    yield put({ type: "SENSOR_CREATE_SUCCESS", sensor });
  } catch (error) {
    yield put({ type: "SENSOR_CREATE_FAILURE", error });
  }
}
function* sensorDeleteSaga(action) {
  try {
    const sensorAPI = new API("device");
    yield call(sensorAPI.delete, action.payload.id);
    yield put({ type: "SENSOR_DELETE_SUCCESS" , id: action.payload.id });
  } catch (error) {
    yield put({ type: "SENSOR_DELETE_FAILURE", error });
  }
}

function* actuatorReadSaga(action) {
  try {
    const actuatorsAPI = new API("device");
    const response = yield call(actuatorsAPI.getAll, action.payload);
    const actuators = response.data;
    yield put({ type: "ACTUATOR_READ_SUCCESS", actuators });
  } catch (error) {
    yield put({ type: "ACTUATOR_READ_FAILURE", error });
  }
}

function* actuatorCreateSaga(action) {
  try {
    const actuatorsAPI = new API("device");
    const response = yield call(actuatorsAPI.create, action.payload);
    const actuator = response.data;
    yield put({ type: "ACTUATOR_CREATE_SUCCESS", actuator });
  } catch (error) {
    yield put({ type: "ACTUATOR_CREATE_FAILURE", error });
  }
}
function* actuatorDeleteSaga(action) {
  try {
    const actuatorsAPI = new API("device");
    yield call(actuatorsAPI.delete, action.payload.id);
    yield put({ type: "ACTUATOR_DELETE_SUCCESS" , id: action.payload.id });
  } catch (error) {
    yield put({ type: "ACTUATOR_DELETE_FAILURE", error });
  }
}
