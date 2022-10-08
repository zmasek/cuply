const initialDashboardState = {
  fetching: false,
  error: null,
  structure: null,
};

export function dashboardReducer(state = initialDashboardState, action) {
  switch (action.type) {
    case "DASHBOARD_READ_REQUEST":
      return { ...state, fetching: true, error: null };
    case "DASHBOARD_READ_SUCCESS":
      return { ...state, fetching: false, structure: action.structure };
    case "DASHBOARD_READ_FAILURE":
      return { ...state, fetching: false, structure: null, error: action.error };
    default:
      return state;
  }
}

const initialProfileState = {
  fetching: false,
  error: null,
  remoteToken: "",
  id: null,
};

export function profileReducer(state = initialProfileState, action) {
  switch (action.type) {
    case "PROFILE_READ_REQUEST":
      return { ...state, fetching: true, error: null };
    case "PROFILE_READ_SUCCESS":
      return { ...state, fetching: false, remoteToken: action.remoteToken, id: action.id };
    case "PROFILE_READ_FAILURE":
      return { ...state, fetching: false, remoteToken: null, id: null, error: action.error };
    case "PROFILE_UPDATE_REQUEST":
      return { ...state, fetching: true, error: null };
    case "PROFILE_UPDATE_SUCCESS":
      return { ...state, fetching: false, remoteToken: action.remoteToken };
    case "PROFILE_UPDATE_FAILURE":
      return { ...state, fetching: false, remoteToken: null, error: action.error };
    case "TOKEN_UPDATE":
      return { ...state, fetching: false, remoteToken: action.remoteToken };
    default:
      return state;
  }
}

const initialPlantsState = {
  fetching: false,
  error: null,
  plants: [],
  treleId: null,
  id: null,
};

export function plantsReducer(state = initialPlantsState, action) {
  switch (action.type) {
    case "PLANT_READ_REQUEST":
      return { ...state, fetching: true, error: null };
    case "PLANT_READ_SUCCESS":
      return { ...state, fetching: false, plants: action.plants };
    case "PLANT_READ_FAILURE":
      return { ...state, fetching: false, plants: [], error: action.error };
    case "PLANT_CREATE_REQUEST":
      return { ...state, fetching: true, error: null };
    case "PLANT_CREATE_SUCCESS":
      return {
        ...state,
        fetching: false,
        plants: state.plants.concat(action.plant),
        remoteId: action.remoteId
      };
    case "PLANT_CREATE_FAILURE":
      return { ...state, fetching: false, remoteId: null, error: action.error };
    case "PLANT_DELETE_REQUEST":
      return { ...state, fetching: true, error: null };
    case "PLANT_DELETE_SUCCESS":
      return {
        ...state,
        plants: state.plants.filter((item) => { return item.id !== action.id }),
        fetching: false
      };
    case "PLANT_DELETE_FAILURE":
      return { ...state, fetching: false, error: action.error };
    default:
      return state;
  }
}

const initialLoginState = {
  fetching: false,
  error: null,
  accessToken: window.localStorage.getItem('accessToken', ""),
  refreshToken: window.localStorage.getItem('refreshToken', ""),
};

export function loginReducer(state = initialLoginState, action) {
  switch (action.type) {
    case "LOGIN_REQUEST":
      return { ...state, fetching: true, error: null };
    case "LOGIN_SUCCESS":
      window.localStorage.setItem('accessToken', action.accessToken);
      window.localStorage.setItem('refreshToken', action.refreshToken);
      return { ...state, fetching: false, accessToken: action.accessToken, refreshToken: action.refreshToken, error: null };
    case "LOGIN_FAILURE":
      return { ...state, fetching: false, accessToken: "", refreshToken: "", error: action.error };
    default:
      return state;
  }
}
const initialTrendsState = {
  fetching: false,
  error: null,
  trends: {"1":[], "2":[], "3":[]},
};

export function trendsReducer(state = initialTrendsState, action) {
  switch (action.type) {
    case "TRENDS_READ_REQUEST":
      return { ...state, fetching: true, error: null };
    case "TRENDS_READ_SUCCESS":
      let newTrends = {
        ...state.trends,
        [action.payload.device_id]: action.trends,
      }
      return { ...state, fetching: false, trends: newTrends };
    case "TRENDS_READ_FAILURE":
      return { ...state, fetching: false, trends: {}, error: action.error };
    default:
      return state;
  }
}

const initialSensorState = {
  fetching: false,
  error: null,
  sensors: [],
};

export function sensorsReducer(state = initialSensorState, action) {
  switch (action.type) {
    case "SENSOR_READ_REQUEST":
      return { ...state, fetching: true, error: null };
    case "SENSOR_READ_SUCCESS":
      return { ...state, fetching: false, sensors: action.sensors };
    case "SENSOR_READ_FAILURE":
      return { ...state, fetching: false, sensors: [], error: action.error };
    case "SENSOR_CREATE_REQUEST":
      return { ...state, fetching: true, error: null };
    case "SENSOR_CREATE_SUCCESS":
      return {
        ...state,
        fetching: false,
        sensors: state.sensors.concat(action.sensor),
        error: null
      };
    case "SENSOR_CREATE_FAILURE":
      return { ...state, fetching: false, error: action.error };
    case "SENSOR_DELETE_REQUEST":
      return { ...state, fetching: true, error: null };
    case "SENSOR_DELETE_SUCCESS":
      return {
        ...state,
        fetching: false,
        error: null,
        sensors: state.sensors.filter((item) => { return item.id !== action.id }),
      };
    case "SENSOR_DELETE_FAILURE":
      return { ...state, fetching: false, error: action.error };
    default:
      return state;
  }
}

const initialActuatorState = {
  fetching: false,
  error: null,
  actuators: [],
};

export function actuatorsReducer(state = initialActuatorState, action) {
  switch (action.type) {
    case "ACTUATOR_READ_REQUEST":
      return { ...state, fetching: true, error: null };
    case "ACTUATOR_READ_SUCCESS":
      return { ...state, fetching: false, actuators: action.actuators };
    case "ACTUATOR_READ_FAILURE":
      return { ...state, fetching: false, actuators: [], error: action.error };
    case "ACTUATOR_CREATE_REQUEST":
      return { ...state, fetching: true, error: null };
    case "ACTUATOR_CREATE_SUCCESS":
      return {
        ...state,
        fetching: false,
        actuators: state.actuators.concat(action.actuator),
        error: null
      };
    case "ACTUATOR_CREATE_FAILURE":
      return { ...state, fetching: false, error: action.error };
    case "ACTUATOR_DELETE_REQUEST":
      return { ...state, fetching: true, error: null };
    case "ACTUATOR_DELETE_SUCCESS":
      return {
        ...state,
        fetching: false,
        error: null,
        actuators: state.actuators.filter((item) => { return item.id !== action.id }),
      };
    case "ACTUATOR_DELETE_FAILURE":
      return { ...state, fetching: false, error: action.error };
    default:
      return state;
  }
}
