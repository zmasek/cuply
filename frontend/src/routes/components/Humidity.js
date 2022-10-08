import React from "react";
import * as d3 from "d3";
import * as VanillaTilt from "vanilla-tilt";
import { DragSource } from "react-dnd";
import "./Humidity.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";


class Humidity extends React.Component {
  state = {
    lastState: "",
    readings: [<div key={1}></div>, <div key={2}></div>, <div key={3}></div>],
    value: null,
  };
  deleteSensor = (event) => {
    let payload = {id: this.props.id};
    this.props.deleteSensor(payload);
  }
  createWidget(container, config) {
    return this.props.type;
  }
  renderList() {
    return this.state.readings;
  }
  updateReadings(gauge, value) {
    new Bubble(this.bubbles, value, this.bubblesLocation);
  }
  updateLogs(reading) {
    const currentReadings = this.state.readings;
    if (this.state.lastState !== reading["state"]) {
      this.setState({ value: reading["median"] });
      this.setState({ lastState: reading["state"] });
      currentReadings.pop();
      let elementType = "";
      switch (reading["state"]) {
        case "medium":
          elementType = "success";
          break;
        case "high":
          elementType = "warning";
          break;
        case "low":
          elementType = "warning";
          break;
        case "very_high":
          elementType = "danger";
          break;
        case "very_low":
          elementType = "danger";
          break;
        default:
          break;
      }
      let elementState = reading["state"].replace("_", " ");
      let elementTimestamp = new Date(reading["timestamp"]).toLocaleString();
      let cls = `list-group-item list-group-item-${elementType}`;
      let clsBadge = `text-uppercase mb-1 badge badge-${elementType} mr-1`;
      let element = (
        <li className={cls} key={elementTimestamp}>
          <p className={clsBadge}>{elementState}</p>
          <small>{elementTimestamp}</small><br />
        </li>
      );
      currentReadings.unshift(element);
      this.setState({ readings: currentReadings });
    }
  }
  componentDidMount() {
    const configuration = {};
    this.bubbles = this.createWidget(`#${this.props.type}`, configuration);
    VanillaTilt.init(this.rootNode, {
      max: 25,
      speed: 400
    });
  }
  componentDidUpdate(prevProps) {
    let data = this.props.data.filter(item => item["name"] === this.props.type)[0];
    if (data !== undefined && data.length !== 0) {
      this.updateReadings(this.bubbles, data["median"]);
      this.updateLogs(data);
    }
  }
  render() {
    // const connectDragSource = this.props.connectDragSource;
    const { connectDragSource, type, editable } = this.props;
    const classString = `card card-width ${editable ? "no-pointer-events" : ""}`;
    return connectDragSource(
      <div ref={node => (this.rootNode = node)} className={classString}>
        {editable ? "" : <button className="btn btn-danger ml-auto"><FontAwesomeIcon icon={faTimes} /></button>}
        <div className="d-flex justify-content-center text-right mt-3">
          <div ref={node => (this.bubblesLocation = node)} id={this.props.type}></div>
          <div id="humidityInfoBubble">{this.state.value}%</div>
        </div>
        <div className="card-body">
          <h5 className="card-title text-capitalize">{type}</h5>
          <h6 className="card-subtitle mb-2 text-muted text-capitalize">
            {type} Sensor Output
          </h6>
          <p className="card-text">
            This widget checks the level of {type.toLowerCase()} in the greenhouse.
          </p>
        </div>
        <ul className="list-group list-group-flush">{this.renderList()}</ul>
        <div className="card-footer">
          <button className="btn btn-danger float-sm-right" onClick={this.deleteSensor}>Delete</button>
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

export default DragSource("card", cardSource, collect)(Humidity);


class Bubble {
  constructor(location, value, bubblesLocation) {
    this.bubbleSpan = undefined;
    this.color = "rgba(0, 0, 125, 0.5)";
    this.location = document.getElementById(location);
    this.innerHeight = bubblesLocation.getBoundingClientRect().height;
    this.innerWidth = bubblesLocation.getBoundingClientRect().width;

    this.posY = this.randomNumber(this.innerHeight - 20, 20);
    this.posX = this.randomNumber(this.innerWidth - 20, 20);

    this.handleNewBubble();
    this.bubbleSpan.style.top = this.posY + "px";
    this.bubbleSpan.style.left = this.posX + "px";

    // setting height and width of the bubble
    this.height = value;
    this.width = this.height;

    this.bubbleEnd.call(this.bubbleSpan, this.randomNumber(6000, 3000));
  }

  // creates and appends a new bubble in the DOM
  handleNewBubble() {
    this.bubbleSpan = document.createElement("span");
    this.bubbleSpan.classList.add("bubble");
    this.location.append(this.bubbleSpan);
    this.handlePosition();
    //this.bubbleSpan.addEventListener("click", this.bubbleEnd);
  }

  handlePosition() {
    // positioning the bubble in different random X and Y
    const randomY = this.randomNumber(60, -60);
    const randomX = this.randomNumber(60, -60);

    this.bubbleSpan.style.backgroundColor = this.color;
    this.bubbleSpan.style.height = this.height + "px";
    this.bubbleSpan.style.width = this.height + "px";

    this.posY = this.randomNumber(this.innerHeight - 20, 20);
    this.posX = this.randomNumber(this.innerWidth - 20, 20);

    this.bubbleSpan.style.top = this.posY + "px";
    this.bubbleSpan.style.left = this.posX + "px";

    const randomSec = this.randomNumber(4000, 200);
    setTimeout(this.handlePosition.bind(this), randomSec); // calling for re-position of bubble
  }

  randomNumber(max, min) {
    return Math.floor(Math.random() * (max - min + 1) + min);
  }


  bubbleEnd(removingTime = 0) {
    setTimeout(
      () => {
        this.classList.add("bubble--bust");
      },
      removingTime === 0 ? removingTime : removingTime - 100
    );

    setTimeout(() => {
      this.remove();
      //new Bubble();
    }, removingTime);
  }
}
