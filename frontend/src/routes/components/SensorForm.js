import React from "react";
import "./SensorForm.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

export default class SensorForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      name: "",
      pin: "",
      signal: "",
      fsm_class: ""
    };
  }
  addSensor = (event) => {
    let payload = {
      name: this.state.name,
      pin: this.state.pin,
      signal: this.state.signal,
      fsm_class: this.state.fsm_class
    };
    this.props.createSensor(payload);
    // the next one is probably wrong, it needs to execute only if the previous one is successful
    // I also need id from the created sensor to construct the dashboard payload
    // let newStructure = {...this.props.structure};
    // newStructure.structure = [...this.props.structure.structure, {id: returnedId, signal: this.state.name}];
    // this.props.updateStructure(newStructure);
    this.props.toggle();
  }
  onChange = (event) => {
    this.setState({
      [event.target.id]: event.target.value
    });
  };
  render() {
    return (
      <div className="custom-modal">
        <div className="obfuscator" onClick={this.props.toggle}></div>
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">Add sensor</h5>
              <button type="button" className="close" onClick={this.props.toggle}>
                <FontAwesomeIcon icon={faTimes} />
              </button>
            </div>
            <div className="modal-body">
              <form>
                <div className="form-group">
                  <label htmlFor="name" className="col-form-label">Name:</label>
                  <input type="text" onChange={this.onChange} className="form-control" id="name" value={this.state.name} />
                </div>
                <div className="form-group">
                  <label htmlFor="pin" className="col-form-label">Pin:</label>
                  <input type="text" onChange={this.onChange} className="form-control" id="pin" value={this.state.pin} />
                  <small id="pinHelp" class="form-text text-muted">Pin where the device connects. E.g. D54, A1. Not needed for I2C kind.</small>
                </div>
                <div className="form-group">
                  <label htmlFor="signal" className="col-form-label">Signal:</label>
                  <input type="text" onChange={this.onChange} className="form-control" id="signal" value={this.state.signal} />
                  <small id="signalHelp" class="form-text text-muted">Analog or Digital.</small>
                </div>
                <div className="form-group">
                  <label htmlFor="kind" className="col-form-label">Kind:</label>
                  <input type="text" onChange={this.onChange} className="form-control" id="kind" value={this.state.kind} />
                  <small id="kindHelp" class="form-text text-muted">Sensor, Actuator, I2C or PWM.</small>
                </div>
              </form>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={this.props.toggle}>Close</button>
              <button type="button" className="btn btn-primary" onClick={this.addSensor}>Add sensor</button>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
