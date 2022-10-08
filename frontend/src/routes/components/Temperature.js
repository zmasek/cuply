import React from "react";
import * as d3 from "d3";
import * as VanillaTilt from "vanilla-tilt";
import { DragSource } from "react-dnd";
import "./Temperature.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

class Temperature extends React.Component {
  state = {
    lastState: "",
    readings: [<div key={1}></div>, <div key={2}></div>, <div key={3}></div>]
  };
  deleteSensor = (event) => {
    let payload = {id: this.props.id};
    this.props.deleteSensor(payload);
  }
  createWidget(container, configuration) {
    let thermometer = new Thermometer({
      mercuryColor: "rgb(58,60,180)"
    });
    thermometer.render(container, configuration.currentTemp, configuration.minTemp, configuration.maxTemp);
    return thermometer;
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
    gauge.setCurrentValue(value);
  }
  componentDidMount() {
    const configuration = {
      currentTemp: 15,
      minTemp: 10,
      maxTemp: 20,
    };
    this.gauge = this.createWidget(`#${this.props.type}`, configuration);
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
        <div className="text-center mt-3">
          <div id={this.props.type}></div>
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

export default DragSource("card", cardSource, collect)(Temperature);










let Thermometer = (function(d3) {

  "use strict";

  function Thermometer(config) {
    this._config = {};
    _extend(this._config, Thermometer.defaults);

    if (config) {
      _extend(this._config, config);
    }
  }

  Thermometer.defaults = {
    width: 80,
    height: 160,
    mercuryColor: "rgb(58,60,180)",
    bulbShineColor: "rgb(230, 200, 200)",
    borderColor: "rgb(136, 136, 136)",
    borderWidth: 1,
    backgroundColor: "rgb(255, 255, 255)",
    bulbRadius: 18,
    tubeWidth: 18.5
  };

  Thermometer.classPrefix = 'thermometer';


  Thermometer.prototype.render = function(container, currentTemp, minTemp, maxTemp) {

    var bottomY = this._config.height - 5,
      topY = 5;

    this._dim = {
      bottomY: bottomY,
      topCy: topY + this._config.tubeWidth / 2,
      topY: topY + this._config.tubeWidth / 2,
      bulbCx: this._config.width / 2,
      bulbCy: bottomY - this._config.bulbRadius
    };

    this._value = {
      current: currentTemp,
      min: minTemp,
      max: maxTemp
    };

    d3.select(container)
      .select("svg")
      .remove();

    this._svg = d3.select(container)
      .append("svg")
      .attr("width", this._config.width)
      .attr("height", this._config.height);

    _defineBulbGradient.call(this);
    _renderTube.call(this);
    _initAxis.call(this);
    _renderExtremes.call(this);
    _renderMercury.call(this);
    _renderAxis.call(this);

  };


  Thermometer.prototype.destroy = function() {
    var svg = this._svg.node();
    svg.parentNode.removeChild(svg);
  };


  Thermometer.prototype.setMaxValue = function(value) {
    this._value.max = value;
    _update.call(this);
  };


  Thermometer.prototype.setMinValue = function(value) {
    this._value.min = value;
    _update.call(this);
  };


  Thermometer.prototype.setCurrentValue = function(value) {
    this._value.current = value;

    if (value < this._value.min) {
      this.setMinValue(value);
    } else if (value > this._value.max) {
      this.setMaxValue(value);
    } else {
      _adjustMercuryHeight.call(this);
    }
  };


  function _update() {
    _initAxis.call(this);
    _renderAxis.call(this);
    _updateMinimumMark.call(this);
    _updateMaximumMark.call(this);
    _adjustMercuryHeight.call(this);
  }


  function _adjustMercuryHeight() {
     /*
      var colorScale = d3.scaleLinear().domain([0, 100]).range(["red", "blue"]);
      .style("fill", function() {
        return colorScale();
      }); // HERE gradient 004dff ff4c01*/
    var tubeFill_bottom = this._dim.bulbCy,
      tubeFill_top = this._axisData.scale(this._value.current);

    // Rect element for the red mercury column
    this._svg
      .select("." + _createCssClass.call(this, "mercury", "column"))
      .attr("y", tubeFill_top)
      .attr("height", tubeFill_bottom - tubeFill_top);
  }


  function _updateMinimumMark() {
    this._svg
      .select("." + _createCssClass.call(this, "min", "line"))
      .attr("y1", this._axisData.scale(this._value.min))
      .attr("y2", this._axisData.scale(this._value.min));

    // Max temperature value
    this._svg
      .select("." + _createCssClass.call(this, "min", "label"))
      .attr("y", this._axisData.scale(this._value.min) + 4);
  }


  function _updateMaximumMark() {
    this._svg
      .select("." + _createCssClass.call(this, "max", "line"))
      .attr("y1", this._axisData.scale(this._value.max))
      .attr("y2", this._axisData.scale(this._value.max));

    // Max temperature value
    this._svg
      .select("." + _createCssClass.call(this, "max", "label"))
      .attr("y", this._axisData.scale(this._value.max) - 4);
  }


  function _initAxis() {
    var step = 5;

    // Determine a suitable range of the temperature scale
    var domain = [
      step * Math.floor(this._value.min / step),
      step * Math.ceil(this._value.max / step)
    ];

    if (_exceedsMinThreshold(this._value.min, domain[0], step)) {
      domain[0] -= step;
    }

    if (_exceedsMaxThreshold(this._value.max, domain[1], step)) {
      domain[1] += step;
    }

    // Values to use along the scale ticks up the thermometer
    var ticksAt = d3.range((domain[1] - domain[0]) / step + 1).map(function (v) {
      return domain[0] + v * step;
    });

    var scale = d3.scaleLinear()
      .range([
        this._dim.bulbCy - this._config.bulbRadius / 2 - 8.5,
        this._dim.topCy
      ])
      .domain(domain);

    this._axisData = {
      step: step,
      domain: domain,
      tickValues: ticksAt,
      scale: scale
    };
  }


  function _renderAxis() {
    var className = _createCssClass.call(this, "temperature", "axis");

    var axis = d3.axisLeft(this._axisData.scale)
      .tickSizeInner(7)
      .tickSizeOuter(0)
      .tickValues(this._axisData.tickValues);

    // remove any old axis
    this._svg
      .select("." + className)
      .remove();

    // Add the axis to the image
    var svgAxis = this._svg.append("g")
      .attr("class", className)
      .attr("transform", "translate(" + (this._config.width / 2 - this._config.tubeWidth / 2) + ",0)")
      .call(axis);

    // Format text labels
    svgAxis.selectAll(".tick text")
      .style("fill", "#777777")
      .style("font-size", "10px");

    // Set main axis line to no stroke or fill
    svgAxis.select("path")
      .style("stroke", "none")
      .style("fill", "none");

    // Set the style of the ticks
    svgAxis.selectAll(".tick line")
      .style("stroke", this._config.borderColor)
      .style("shape-rendering", "crispEdges")
      .style("stroke-width", this._config.borderWidth + "px");
  }


  function _renderExtremes() {
    // Max and min temperature lines
    [this._value.min, this._value.max].forEach(function (t) {

      var isMax = t === this._value.max,
        label = (isMax ? "max" : "min"),
        textCol = (isMax ? "rgb(230, 0, 0)" : "rgb(0, 0, 230)"),
        textOffset = (isMax ? -4 : 4);

      this._svg
        .append("line")
        .attr("class", _createCssClass.call(this, label, "line"))
        .attr("x1", this._config.width / 2 - this._config.tubeWidth / 2)
        .attr("x2", this._config.width / 2 + this._config.tubeWidth / 2 + 22)
        .attr("y1", this._axisData.scale(t))
        .attr("y2", this._axisData.scale(t))
        .style("stroke", this._config.borderColor)
        .style("stroke-width", this._config.borderWidth + "px")
        .style("shape-rendering", "crispEdges");

      this._svg
        .append("text")
        .attr("class", _createCssClass.call(this, label, "label"))
        .attr("x", this._config.width / 2 + this._config.tubeWidth / 2 + 2)
        .attr("y", this._axisData.scale(t) + textOffset)
        .attr("dy", isMax ? null : "0.72em")
        .text(label)
        .style("fill", textCol)
        .style("font-size", "10px");

    }, this);
  }


  function _renderMercury() {
    var tubeFill_bottom = this._dim.bulbCy,
      tubeFill_top = this._axisData.scale(this._value.current);

    var svgDefs = this._svg.append('defs');
    var mainGradient = svgDefs.append('linearGradient')
        .attr('id', 'mainGradient')
        .attr("x1", "0%")
        .attr("x2", "0%")
        .attr("y1", "0%")
        .attr("y2", "100%");

    mainGradient.append('stop')
        .attr('class', 'stop-top')
        .attr('offset', '0');

    mainGradient.append('stop')
      .attr('class', 'stop-middle')
      .attr('offset', '0.5');

    mainGradient.append('stop')
        .attr('class', 'stop-bottom')
        .attr('offset', '1');

    // Rect element for the red mercury column
    this._svg
      .append("rect")
      .attr("class", _createCssClass.call(this, "mercury", "column"))
      .classed('filled', true)
      .attr("x", this._config.width / 2 - (this._config.tubeWidth - 8) / 2)
      .attr("y", tubeFill_top)
      .attr("width", this._config.tubeWidth - 8)
      .attr("height", tubeFill_bottom - tubeFill_top)
      .style("shape-rendering", "crispEdges")
      //.style("fill", this._config.mercuryColor);


    // Main thermometer bulb fill
    this._svg
      .append("circle")
      .attr("r", this._config.bulbRadius - 5)
      .attr("cx", this._dim.bulbCx)
      .attr("cy", this._dim.bulbCy)
      .style("fill", "url(#" + Thermometer.classPrefix + "-bulb-gradient)")
      .style("stroke", this._config.mercuryColor)
      .style("stroke-width", "2px");
  }


  function _defineBulbGradient() {
    var defs = this._svg.append("defs");

    // Define the radial gradient for the bulb fill colour
    var bulbGradient = defs.append("radialGradient")
      .attr("id", Thermometer.classPrefix + "-bulb-gradient")
      .attr("cx", "50%")
      .attr("cy", "50%")
      .attr("r", "50%")
      .attr("fx", "50%")
      .attr("fy", "50%");

    bulbGradient.append("stop")
      .attr("offset", "0%")
      .style("stop-color", this._config.bulbShineColor);

    bulbGradient.append("stop")
      .attr("offset", "90%")
      .style("stop-color", this._config.mercuryColor);
  }


  function _renderTube() {
    // Circle element for rounded tube top

    this._svg
      .append("circle")
      .attr("r", this._config.tubeWidth / 2)
      .attr("cx", this._config.width / 2)
      .attr("cy", this._dim.topCy)
      .style("fill", this._config.backgroundColor)
      .style("stroke", this._config.borderColor)
      .style("stroke-width", this._config.borderWidth + "px");


    // Rect element for tube
    this._svg
      .append("rect")
      .attr("x", this._config.width / 2 - this._config.tubeWidth / 2)
      .attr("y", this._dim.topCy)
      .attr("height", this._dim.bulbCy - this._dim.topCy)
      .attr("width", this._config.tubeWidth)
      .style("shape-rendering", "crispEdges")
      .style("fill", this._config.backgroundColor)
      .style("stroke", this._config.borderColor)
      .style("stroke-width", this._config.borderWidth + "px");


    // White fill for rounded tube top circle element
    // to hide the border at the top of the tube rect element
    this._svg
      .append("circle")
      .attr("r", this._config.tubeWidth / 2 - this._config.borderWidth / 2)
      .attr("cx", this._config.width / 2)
      .attr("cy", this._dim.topCy)
      .style("fill", this._config.backgroundColor)
      .style("stroke", "none");


    // Main bulb of thermometer (empty), white fill
    this._svg
      .append("circle")
      .attr("r", this._config.bulbRadius)
      .attr("cx", this._dim.bulbCx)
      .attr("cy", this._dim.bulbCy)
      .style("fill", this._config.backgroundColor)
      .style("stroke", this._config.borderColor)
      .style("stroke-width", this._config.borderColor + "px");


    // Another rect element for empty tube (white fill)
    // to cover over the top border of the main bulb circle.
    this._svg
      .append("rect")
      .attr("x", this._config.width / 2 - (this._config.tubeWidth - this._config.borderWidth) / 2)
      .attr("y", this._dim.topCy)
      .attr("height", this._dim.bulbCy - this._dim.topCy)
      .attr("width", this._config.tubeWidth - this._config.borderWidth)
      .style("shape-rendering", "crispEdges")
      .style("fill", this._config.backgroundColor)
      .style("stroke", "none");
  }


  function _createCssClass () {
    var className = Thermometer.classPrefix,
      n = arguments.length,
      i = 0;
    while (i < n) {
      className += ("-" + arguments[i++]);
    }
    return className;
  }


  function _exceedsMinThreshold(value, min, step) {
    return value - min < 0.66 * step;
  }


  function _exceedsMaxThreshold(value, max, step) {
    return max - value < 0.66 * step;
  }


  function _extend(baseObj, extendingObj) {
    var keys = Object.keys(extendingObj);
    keys.forEach(function(key) {
      baseObj[key] = extendingObj[key];
    });
  }


  return Thermometer;

})(d3);
