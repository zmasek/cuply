import React from "react";
import { connect } from "react-redux";
import { DropTarget } from "react-dnd";
import Light from "./components/Light";
import Water from "./components/Water";
import Humidity from "./components/Humidity";
import Temperature from "./components/Temperature";
import SensorForm from "./components/SensorForm";
import "./Sensors.css";

const mapStateToProps = state => {
  return {
    fetching: state.sensorsReducer.fetching,
    sensors: state.sensorsReducer.sensors,
    error: state.sensorsReducer.error,
    accessToken: state.loginReducer.accessToken,
  };
};
const mapDispatchToProps = dispatch => {
  return {
    readSensors: (payload) => {
      return dispatch({ type: "SENSOR_READ_REQUEST", payload });
    },
    createSensor: (payload) => {
      return dispatch({ type: "SENSOR_CREATE_REQUEST", payload });
    },
    deleteSensor: (payload) => {
      return dispatch({ type: "SENSOR_DELETE_REQUEST", payload });
    },
  };
};

class Sensors extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      modalState: false,
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
    let data = JSON.parse(e.data).filter(reading => reading.fsm_class !== "DigitalActuator");
    this.setState({ data: data });
  };

  componentDidMount() {
    // might need to revisit since it's an object now
    if (this.props.sensors.length === 0) {
      let payload = {"fsm_class!": "DigitalActuator"};
      this.props.readSensors(payload);
    }
    this.sensorSocket = new WebSocket(
      "ws://" + window.location.host + "/microcontroller/"
    );
    this.sensorSocket.addEventListener("message", this.parseEvent);
    document.title = 'Sensors | Cuply';
  }
  componentDidUpdate(prevProps) {
    if (prevProps.accessToken !== this.props.accessToken) {
      let payload = {"fsm_class!": "DigitalActuator"};
      this.props.readSensors(payload);
    }
  }
  componentWillUnmount() {
    this.sensorSocket.removeEventListener("message", this.parseEvent);
    this.sensorSocket.close();
    this.sensorSocket = null;
  }

  getCards = row => {
    return this.props.sensors.filter(element => {
      return element["row"] === row;
    });
  };

  createLayout = () => {
    const canProceed = this.props.sensors.length !== 0;
    if (canProceed) {
      let button = this.state.editable ?
      ""
      :
      (<div key="addSensor" style={{width: "18rem"}} className="card align-items-center justify-content-center border-color-dark border-style new-sensor" onClick={this.toggleModal}>
        <span className="text-muted" style={{fontSize: "1.5em"}}>Add sensor</span>
      </div>);
      let cards = [];
      for (const card of this.props.sensors) {
        let component = null;
        if (card.name.toLowerCase().includes("water")) {
          component = <Water
            editable={this.state.editable}
            type={card.name}
            id={card.id}
            key={card.id}
            data={this.state.data}
            deleteSensor={this.props.deleteSensor.bind(this)}
          />
        } else if (card.name.toLowerCase().includes("humidity")) {
          component = <Humidity
            editable={this.state.editable}
            type={card.name}
            id={card.id}
            key={card.id}
            data={this.state.data}
            deleteSensor={this.props.deleteSensor.bind(this)}
          />
        } else if (card.name.toLowerCase().includes("light")) {
          component = <Light
            editable={this.state.editable}
            type={card.name}
            id={card.id}
            key={card.id}
            data={this.state.data}
            deleteSensor={this.props.deleteSensor.bind(this)}
          />;
        } else if (card.name.toLowerCase().includes("temperature")) {
          component = <Temperature
            editable={this.state.editable}
            type={card.name}
            id={card.id}
            key={card.id}
            data={this.state.data}
            deleteSensor={this.props.deleteSensor.bind(this)}
          />;
        }
        cards.push(component);
      }
      cards.push(button);
      return cards;
    }
  };
  changeEditable = (e) => {
    const current = this.state.editable;
    this.setState({ editable: !current });
  };
  toggleModal = (e) => {
    this.setState({modalState: !this.state.modalState});
  }
  render() {
    const connectDropTarget = this.props.connectDropTarget;
    return connectDropTarget(
      <div>
        { this.state.modalState ? <SensorForm createSensor={this.props.createSensor.bind(this)} toggle={this.toggleModal.bind(this)} /> : null }
        <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
          <h1 className="h2">Sensors</h1>
          <button className="btn btn-success" onClick={this.changeEditable}>{this.state.editable ? "Edit": "Save"}</button>
        </div>
        <div className="card-deck" onDrop={this.onDrop}>
          {this.createLayout()}
        </div>
      </div>
    );
  }
}

const SensorsRedux = connect(
  mapStateToProps,
  mapDispatchToProps
)(Sensors);
const dropSource = {};
function collect(connect, monitor) {
  return {
    connectDropTarget: connect.dropTarget()
  };
}
export default DropTarget("card", dropSource, collect)(SensorsRedux);
