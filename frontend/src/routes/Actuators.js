import React from "react";
import { connect } from "react-redux";
import { DropTarget } from "react-dnd";
import State from "./components/State";
import ActuatorForm from "./components/ActuatorForm";
import "./Actuators.css";

const mapStateToProps = state => {
  return {
    // it might be better to have a actuator type for devices
    fetching: state.actuatorsReducer.fetching,
    actuators: state.actuatorsReducer.actuators,
    error: state.actuatorsReducer.error,
    accessToken: state.loginReducer.accessToken,
  };
};
const mapDispatchToProps = dispatch => {
  return {
    readActuators: (payload) => {
      return dispatch({ type: "ACTUATOR_READ_REQUEST", payload });
    },
    createActuator: (payload) => {
      return dispatch({ type: "ACTUATOR_CREATE_REQUEST", payload });
    },
    deleteActuator: (payload) => {
      return dispatch({ type: "ACTUATOR_DELETE_REQUEST", payload });
    },
  };
};

class Actuators extends React.Component {
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
    let data = JSON.parse(e.data).filter(reading => reading.kind === "actuator");
    this.setState({ data: data });
  };

  componentDidMount() {
    // might need to revisit since it's an object now
    if (this.props.actuators.length === 0) {
      let payload = {fsm_class: "DigitalActuator"};
      this.props.readActuators(payload);
    }
    this.actuatorSocket = new WebSocket(
      "ws://" + window.location.host + "/microcontroller/"
    );
    this.actuatorSocket.addEventListener("message", this.parseEvent);
    document.title = 'Actuators | Cuply';
  }
  componentDidUpdate(prevProps) {
    if (prevProps.accessToken !== this.props.accessToken) {
      let payload = {fsm_class: "DigitalActuator"};
      this.props.readActuators(payload);
    }
  }
  componentWillUnmount() {
    this.actuatorSocket.removeEventListener("message", this.parseEvent);
    this.actuatorSocket.close();
    this.actuatorSocket = null;
  }

  getCards = row => {
    return this.props.actuators.filter(element => {
      return element["row"] === row;
    });
  };

  createLayout = () => {
    const canProceed = this.props.actuators.length !== 0;
    if (canProceed) {
      let button = this.state.editable ?
      ""
      :
      (<div key="addActuator" style={{width: "18rem"}} className="card align-items-center justify-content-center border-color-dark border-style new-actuator" onClick={this.toggleModal}>
        <span className="text-muted" style={{fontSize: "1.5em"}}>Add actuator</span>
      </div>);
      let cards = [];
      for (const card of this.props.actuators) {
        cards.push(
          <State
            editable={this.state.editable}
            type={card.name}
            parent={card.parent}
            image={card.imageUrl}
            id={card.id}
            key={card.id}
            data={this.state.data}
            deleteActuator={this.props.deleteActuator.bind(this)}
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
  toggleModal = (e) => {
    this.setState({modalState: !this.state.modalState});
  }
  render() {
    const connectDropTarget = this.props.connectDropTarget;
    return connectDropTarget(
      <div>
        { this.state.modalState ? <ActuatorForm createActuator={this.props.createActuator.bind(this)} toggle={this.toggleModal.bind(this)} /> : null }
        <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
          <h1 className="h2">Actuators</h1>
          <button className="btn btn-success" onClick={this.changeEditable}>{this.state.editable ? "Edit": "Save"}</button>
        </div>
        <div className="card-deck" onDrop={this.onDrop}>
          {this.createLayout()}
        </div>
      </div>
    );
  }
}

const ActuatorsRedux = connect(
  mapStateToProps,
  mapDispatchToProps
)(Actuators);
const dropSource = {};
function collect(connect, monitor) {
  return {
    connectDropTarget: connect.dropTarget()
  };
}
export default DropTarget("card", dropSource, collect)(ActuatorsRedux);
