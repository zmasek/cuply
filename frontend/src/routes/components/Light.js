import React from "react";
import * as d3 from "d3";
import * as VanillaTilt from "vanilla-tilt";
import { DragSource } from "react-dnd";
import "./Light.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

const COLORS = {
  'Light': ['#000000', '#e0d312'],
  //'temperature': ['#2931c2', '#eb1e0c'],
  //'temperature': ['#004dff', '#1bffe6', '#e4ff1a', '#ff4c01','#810000'],
  //'temperature': ['#004dff', '#810000'],
  'Temperature': ['#004dff', '#ff4c01'],
  //'humidity': ['#dadbe8', '#0a0f6c'],
  'default': ["#e8e2ca", "#3e6c0a"]
};

class Light extends React.Component {
  state = {
    lastState: "",
    readings: [<div key={1}></div>, <div key={2}></div>, <div key={3}></div>]
  };
  deleteSensor = (event) => {
    let payload = {id: this.props.id};
    this.props.deleteSensor(payload);
  }
  createWidget(container, configuration, colors) {
    var gaugeClass = function(container, configuration) {
      var that = {};
      var config = {
        size: 710,
        clipWidth: 200,
        clipHeight: 110,
        ringInset: 20,
        ringWidth: 20,

        pointerWidth: 10,
        pointerTailLength: 5,
        pointerHeadLengthPercent: 0.9,

        minValue: 0,
        maxValue: 10,

        minAngle: -90,
        maxAngle: 90,

        transitionMs: 750,

        majorTicks: 5,
        labelFormat: d3.format("d"),
        labelInset: 10,

        arcColorFn: d3.interpolateHsl(d3.rgb(colors[0]), d3.rgb(colors[1]))
      };
      var range = undefined;
      var r = undefined;
      var pointerHeadLength = undefined;

      var svg = undefined;
      var arc = undefined;
      var scale = undefined;
      var ticks = undefined;
      var tickData = undefined;
      var pointer = undefined;

      function deg2rad(deg) {
        return (deg * Math.PI) / 180;
      }

      function configure(configuration) {
        var prop = undefined;
        for (prop in configuration) {
          config[prop] = configuration[prop];
        }

        range = config.maxAngle - config.minAngle;
        r = config.size / 2;
        pointerHeadLength = Math.round(r * config.pointerHeadLengthPercent);

        // a linear scale that maps domain values to a percent from 0..1
        scale = d3
          .scaleLinear()
          .range([0, 1])
          .domain([config.minValue, config.maxValue]);

        ticks = scale.ticks(config.majorTicks);
        tickData = d3.range(config.majorTicks).map(function() {
          return 1 / config.majorTicks;
        });

        arc = d3
          .arc()
          .innerRadius(r - config.ringWidth - config.ringInset)
          .outerRadius(r - config.ringInset)
          .startAngle(function(d, i) {
            var ratio = d * i;
            return deg2rad(config.minAngle + ratio * range);
          })
          .endAngle(function(d, i) {
            var ratio = d * (i + 1);
            return deg2rad(config.minAngle + ratio * range);
          });
      }
      that.configure = configure;

      function centerTranslation() {
        return "translate(" + r + "," + r + ")";
      }

      function isRendered() {
        return svg !== undefined;
      }
      that.isRendered = isRendered;

      function render(newValue) {
        svg = d3
          .select(container)
          .append("svg:svg")
          .attr("class", "gauge")
          .attr("width", config.clipWidth)
          .attr("height", config.clipHeight);

        var centerTx = centerTranslation();

        var arcs = svg
          .append("g")
          .attr("class", "arc")
          .attr("transform", centerTx);

        arcs
          .selectAll("path")
          .data(tickData)
          .enter()
          .append("path")
          .attr("fill", function(d, i) {
            return config.arcColorFn(d * i);
          })
          .attr("d", arc);

        var lg = svg
          .append("g")
          .attr("class", "label")
          .attr("transform", centerTx);
        lg.selectAll("text")
          .data(ticks)
          .enter()
          .append("text")
          .attr("transform", function(d) {
            var ratio = scale(d);
            var newAngle = config.minAngle + ratio * range;
            return (
              "rotate(" +
              newAngle +
              ") translate(0," +
              (config.labelInset - r) +
              ")"
            );
          })
          .text(config.labelFormat);

        var lineData = [
          [config.pointerWidth / 2, 0],
          [0, -pointerHeadLength],
          [-(config.pointerWidth / 2), 0],
          [0, config.pointerTailLength],
          [config.pointerWidth / 2, 0]
        ];
        var pointerLine = d3.line().curve(d3.curveLinear);
        var pg = svg
          .append("g")
          .data([lineData])
          .attr("class", "pointer")
          .attr("transform", centerTx);

        pointer = pg
          .append("path")
          .attr("d", pointerLine /*function(d) { return pointerLine(d) +'Z';}*/)
          .attr("transform", "rotate(" + config.minAngle + ")");

        update(newValue === undefined ? 0 : newValue);
      }
      that.render = render;
      function update(newValue, newConfiguration) {
        if (newConfiguration !== undefined) {
          configure(newConfiguration);
        }
        var ratio = scale(newValue);
        var newAngle = config.minAngle + ratio * range;
        pointer
          .transition()
          .duration(config.transitionMs)
          .ease(d3.easeElastic)
          .attr("transform", "rotate(" + newAngle + ")");
      }
      that.update = update;

      configure(configuration);

      return that;
    };
    return gaugeClass(container, configuration);
  }
  updateLogs(reading) {
    const currentReadings = this.state.readings;
    if (this.state.lastState !== reading["state"]) {
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
  renderList() {
    return this.state.readings;
  }
  updateReadings(gauge, value) {
    let normalizedValue = value / 100;
    gauge.update(normalizedValue);
  }
  componentDidMount() {
    const configuration = {
      size: 280,
      clipWidth: 280,
      clipHeight: 155,
      ringWidth: 60,
      maxValue: 10,
      transitionMs: 4000
    };
    this.gauge = this.createWidget(`#${this.props.type}`, configuration, COLORS[this.props.type]);
    this.gauge.render();
    this.gauge.update(0);
    VanillaTilt.init(this.rootNode, {
      max: 25,
      speed: 400
    });
  }
  componentDidUpdate(prevProps) {
    let data = this.props.data.filter(item => item["name"] === this.props.type)[0];
    if (data !== undefined && data.length !== 0) {
      this.updateReadings(this.gauge, data["median"]);
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
        <div className="text-right mt-3">
          <div id={this.props.type} className="d-flex justify-content-center align-items-end"></div>
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

export default DragSource("card", cardSource, collect)(Light);
