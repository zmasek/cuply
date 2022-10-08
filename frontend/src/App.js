import React from "react";
import { BrowserRouter as Router, Route } from "react-router-dom";
import { DragDropContext } from "react-dnd";
import HTML5Backend from "react-dnd-html5-backend";
import "./App.css";
import Header from "./layout/Header";
import Sidebar from "./layout/Sidebar";
import Loader from "./layout/Loader";
//import Dashboard from "./routes/Dashboard";
import Sensors from "./routes/Sensors";
import Actuators from "./routes/Actuators";
import Plants from "./routes/Plants";
import Trends from "./routes/Trends";
import Settings from "./routes/Settings";
import { connect } from "react-redux";

const mapStateToProps = state => {
  return {
    fetching: state.plantsReducer.fetching || state.sensorsReducer.fetching || state.actuatorsReducer.fetching || state.profileReducer.fetching || state.loginReducer.fetching || state.trendsReducer.fetching,
  };
};

class App extends React.Component {
  render() {
    return (
      <div>
        {this.props.fetching ? <Loader /> : ""}
        <Router>
          <Header />
          <div className="container-fluid">
            <div className="row">
                <Sidebar />
                <main role="main" className="col-sm-10 ml-sm-auto">
                  <Route path="/" exact component={Sensors} />
                  <Route path="/actuators/" exact component={Actuators} />
                  <Route path="/plants/" exact component={Plants} />
                  <Route path="/trends/" exact component={Trends} />
                  <Route path="/settings/" exact component={Settings} />
                </main>
            </div>
          </div>
        </Router>
      </div>
    );
  }
}
const WrapperApp = DragDropContext(HTML5Backend)(App);
export default connect(
  mapStateToProps,
)(WrapperApp);
