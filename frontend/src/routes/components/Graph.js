import React from "react";
import * as d3 from "d3";
import { connect } from "react-redux";

const mapStateToProps = state => {
  return {
    fetching: state.trendsReducer.fetching,
    trends: state.trendsReducer.trends,
    error: state.trendsReducer.error,
    accessToken: state.loginReducer.accessToken,
  };
};

const mapDispatchToProps = dispatch => {
  return {
    loadTrends: (payload) => {
      return dispatch({ type: "TRENDS_READ_REQUEST", payload });
    },
  };
};

class Graph extends React.Component {
  componentDidMount() {
      let payload = {device_id: this.props.device["id"], timestamp__date: this.getFilterDate(this.props.date)};
      this.props.loadTrends(payload);
  }
  componentDidUpdate(prevProps) {
    if (prevProps.date !== null && (prevProps.date.toString() !== this.props.date.toString())) {
      let payload = {device_id: this.props.device["id"], timestamp__date: this.getFilterDate(this.props.date)};
      this.props.loadTrends(payload);
    }
    const canProceed = Array.isArray(this.props.trends[this.props.device["id"]]);
    if (canProceed) {
      this.createGraph(`#graph${this.props.device["id"]}`, this.props.trends[this.props.device["id"]]);
    }
  }
  getFilterDate(currentDate){
    const year = currentDate.getFullYear();
    const month = (currentDate.getMonth() + 1).toString();
    const normalizedMonth = `${month.length === 1 ? "0" : ""}${month}`;
    const day = currentDate.getDate().toString();
    const normalizedDay = `${day.length === 1 ? "0" : ""}${day}`;
    return `${year}-${normalizedMonth}-${normalizedDay}`
  }
  createGraph(container, data) {
    const values = data.map(item => item.value).sort((a, b) => a - b);
    let min = values[0];
    let max = values[values.length-1];
    let yDomain = [min, max];
    let height = 200;
    let width = 400;
    let margin = {top: 20, right: 30, bottom: 30, left: 40};
    let timeStampFormat = d3.timeFormat("%d %b %Y, %H:%M");
    let y = d3.scaleLinear()
      .domain(yDomain)
      .nice()
      .range([height - margin.bottom, margin.top]);
    let x = d3.scaleUtc()
      .domain(d3.extent(data, d => new Date(d.timestamp)))
      .range([margin.left, width - margin.right])
    const yAxis = g => g
      .attr("transform", `translate(${margin.left},0)`)
      .attr("stroke-width",".3")
      .call(d3.axisLeft(y))
      .call(g => g.select(".domain").remove())
      .call(g => g.select(".tick:last-of-type text").clone()
      .attr("x", 3)
      .attr("text-anchor", "start")
      .attr("font-weight", "normal")
      .text(data.y))
      .attr("font-size", "4px");
    const xAxis = g => g
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x).ticks(width / 80).tickSizeOuter(0).tickFormat(timeStampFormat))
      .attr("font-size", "4px")
      .attr("stroke-width",".5")
      .select(".domain")
      .attr("stroke-width",".3")
      .attr("font-size", "6px");
    let line = d3.line()
      .defined(d => !isNaN(d.value))
      .x(d => x(new Date(d.timestamp)))
      .y(d => y(d.value));
    let svg = d3.select(container).select("svg")
      .remove();
    svg = d3.select(container)
      .append("svg:svg")
      .attr("viewBox", [0, 0, width, height]);

    svg.append("g")
      .call(xAxis);

    svg.append("g")
      .call(yAxis);

    let colorName = "steelblue";
    if (container.includes("2")) {
      colorName = "url(#temperature-gradient)";
      svg.append("linearGradient")
        .attr("id", "temperature-gradient")
        .attr("gradientUnits", "userSpaceOnUse")
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", 0)
        .attr("y2", height)
        .selectAll("stop")
        .data([
          {offset: "0%", color: "#000082"},
          {offset: "20%", color: '#004dff'},
          {offset: "40%", color: '#1bffe6'},
          {offset: "60%", color: '#e4ff1a'},
          {offset: "80%", color: '#ff4c01'},
          {offset: "100%", color: '#810000'}
        ])
        .join("stop")
        .attr("offset", d => d.offset)
        .attr("stop-color", d => d.color);
    }

    svg.append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", colorName)
      .attr("stroke-width", 1)
      .attr("stroke-linejoin", "round")
      .attr("stroke-linecap", "round")
      .attr("d", line);

    let padding = 10;

    svg.append("text")
      .attr("text-anchor", "middle")
      .attr("transform", "translate("+ (padding/2) +","+(height/2)+")rotate(-90)")
      .attr("font-size", "6px")
      .text(`Value${container.includes("2") ? ' °C' : ''}`);

    svg.append("text")
      .attr("text-anchor", "middle")
      .attr("transform", "translate("+ (width/2) +","+(height-(padding/3))+")")
      .attr("font-size", "6px")
      .text("TimeStamp");

    return svg.node();
  }
  render() {
    const tag = `graph${this.props.device["id"]}`;
    return (
      <div>
        <h5>{this.props.device["name"]}</h5>
        <div id={tag}></div>
      </div>
    );
  }
}
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Graph);
