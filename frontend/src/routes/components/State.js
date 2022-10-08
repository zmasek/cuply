import React from "react";
import { DragSource } from "react-dnd";
import "./State.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";
import _ from "lodash";

class State extends React.Component {
  state = {
    lastState: "",
    readings: [<div key={1}></div>, <div key={2}></div>, <div key={3}></div>]
  };
  deleteActuator = (event) => {
    let payload = {id: this.props.id};
    this.props.deleteActuator(payload);
  }
  render() {
    const { connectDragSource, type, editable, parent } = this.props;
    const classString = `card card-width ${editable ? "no-pointer-events" : ""}`;
    let data = this.props.data.filter(item => item["parent"] === parent)[0];
    let checked = false;
    if (data !== undefined && data.length !== 0) {
      checked = data["median"];
    }
    return connectDragSource(
      <div ref={node => (this.rootNode = node)} className={classString}>
        {editable ? "" : <button className="btn btn-danger ml-auto"><FontAwesomeIcon icon={faTimes} /></button>}
        <div className="card-img-top card-img-style">
          <div className={`card-img-custom m-3 ${checked ? '' : 'card-img-off'}`} style={{backgroundImage: `url(${this.props.image})`}}></div>
        </div>
        <div className="card-body">
          <h5 className="card-title text-capitalize">{_.startCase(type)}</h5>
          <h6 className="card-subtitle mb-2 text-muted text-capitalize">
            {_.startCase(type)} Actuator Value
          </h6>
          <p className="card-text">
            This widget shows the state of {_.lowerCase(type)} in the greenhouse. It is controlled by {parent ? parent.toLowerCase() : "time"}.
          </p>
          <div className="d-flex align-items-center">
            <span className="mr-2">Off</span>
              <div className="custom-control custom-switch">
                <input type="checkbox" className="custom-control-input" disabled={editable?"disabled":""} id="customSwitch2" checked={checked} />
                <label className="custom-control-label" htmlFor="customSwitch2"></label>
              </div>
            <span>On</span>
          </div>
        </div>
        <div className="card-footer">
          <button className="btn btn-danger float-sm-right" onClick={this.deleteActuator}>Delete</button>
        </div>
      </div>
    );
  }
}

const cardSource = {
  beginDrag(props) {
    // Return the data describing the dragged item
    const item = { id: props.id };
    return item;
  },

  endDrag(props, monitor, component) {
    if (!monitor.didDrop()) {
      return;
    }

    // When dropped on a compatible target, do something
    // const item = monitor.getItem()
    // const dropResult = monitor.getDropResult()
    // CardActions.moveCardToList(item.id, dropResult.listId)
  }
};

/**
 * Specifies which props to inject into your component.
 */
function collect(connect, monitor) {
  return {
    // Call this function inside render()
    // to let React DnD handle the drag events:
    connectDragSource: connect.dragSource(),
    // You can ask the monitor about the current drag state:
    isDragging: monitor.isDragging()
  };
}

export default DragSource("card", cardSource, collect)(State);
