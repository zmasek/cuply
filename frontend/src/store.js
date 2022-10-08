import { combineReducers, createStore, applyMiddleware, compose } from "redux";
import createSagaMiddleware from "redux-saga";
import { profileReducer, plantsReducer, loginReducer, trendsReducer, sensorsReducer, actuatorsReducer } from "./reducers";
import { rootSaga } from "./sagas";

const sagaMiddleware = createSagaMiddleware();
const store = createStore(
  combineReducers({ profileReducer, plantsReducer, loginReducer, trendsReducer, sensorsReducer, actuatorsReducer }),
  compose(applyMiddleware(sagaMiddleware))
);
sagaMiddleware.run(rootSaga);

export default store;
