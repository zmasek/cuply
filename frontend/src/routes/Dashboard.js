import React from "react";
import { connect } from "react-redux";
import { DropTarget } from "react-dnd";
import Widget from "./components/Widget";
import "./Dashboard.css";

const mapStateToProps = state => {
  return {
    fetching: state.dashboardReducer.fetching,
    structure: state.dashboardReducer.structure,
    error: state.dashboardReducer.error,
    accessToken: state.loginReducer.accessToken,
  };
};

const mapDispatchToProps = dispatch => {
  return {
    loadStructure: () => {
      return dispatch({ type: "DASHBOARD_READ_REQUEST" });
    }
  };
};

class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: {
        light: {
          median_old: 0,
          median: 0,
          timestamp: "2019-06-23T16:56:57.764",
          state: ""
        },
        temperature: {
          median_old: 0,
          median: 0,
          timestamp: "2019-06-23T16:47:30.350",
          state: ""
        },
        humidity: {
          median_old: 0,
          median: 0,
          timestamp: "2019-06-23T16:47:30.350",
          state: ""
        }
      },
      editable: true
    };
  }

  onDrop = component => {
    console.log("dropping", component);
    // const newComponentsList = _.concat([],components, component)
    /*this.setState({
      components: newComponentsList
    })*/
  };

  parseEvent = e => {
    let data = JSON.parse(e.data);
    this.setState({ data: data });
  };

  componentDidMount() {
    if (this.props.structure === null || Object.keys(this.props.structure).length === 0) {
      this.props.loadStructure();
    }
    this.microcontrollerSocket = new WebSocket(
      "ws://" + window.location.host + "/microcontroller/"
    );
    this.microcontrollerSocket.addEventListener("message", this.parseEvent);
    document.title = 'Dashboard | Cuply';
  }
  componentDidUpdate(prevProps) {
    if (prevProps.accessToken !== this.props.accessToken) {
      this.props.loadStructure();
    }
  }
  componentWillUnmount() {
    this.microcontrollerSocket.removeEventListener("message", this.parseEvent);
    this.microcontrollerSocket.close();
    this.microcontrollerSocket = null;
  }

  getCards = row => {
    return this.props.structure.filter(element => {
      return element["row"] === row;
    });
  };

  createLayout = () => {
    const canProceed =
      Array.isArray(this.props.structure) && this.props.structure.length !== 0;
    if (canProceed) {
      let button = this.state.editable ? "":  <div key="addWidget" style={{width: "18rem"}} className="card text-center border-style border-color-dark"><span className="text-muted">Add</span><button className="card btn btn-light align-self-center border-style border-color-dark rounded-circle">+</button></div>;
      let cards = [];
      for (const card of this.props.structure) {
        cards.push(
          <Widget
            editable={this.state.editable}
            type={card.type}
            id={card.id}
            key={card.id}
            data={this.state.data}
          />
        );
      }
      cards.push(button);
      return cards;
    }
  };
  changeEditable = (e) => {
    const current = this.state.editable;
    this.setState({ editable: !current });
  };

  render() {
    const connectDropTarget = this.props.connectDropTarget;
    return connectDropTarget(
      <div>
        <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
          <h1 className="h2">Dashboard</h1>
          <button className="btn btn-success" onClick={this.changeEditable}>{this.state.editable ? "Edit": "Save"}</button>
        </div>
        <div className="card-deck" onDrop={this.onDrop}>
          {this.createLayout()}
        </div>
      </div>
    );
  }
}

const DashboardRedux = connect(
  mapStateToProps,
  mapDispatchToProps
)(Dashboard);
const dropSource = {};
function collect(connect, monitor) {
  return {
    connectDropTarget: connect.dropTarget()
  };
}
export default DropTarget("card", dropSource, collect)(DashboardRedux);
