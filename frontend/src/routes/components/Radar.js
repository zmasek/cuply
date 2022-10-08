import React from "react";
import * as d3 from "d3";
import RadarChart from "./RadarChart";

export default class Radar extends React.Component {
  createRadar(container, data, configuration) {

  }
  componentDidMount() {
    let color = d3.scaleBand()
      .range(["#EDC951","#CC333F","#00A0B0"]);

    let radarChartOptions = {
      width: 400,
      height: 400,
      color: color
    };
    this.radarChart = RadarChart()
    d3.select(`#${this.props.type}`)
      .call(this.radarChart);
    this.radarChart.options(radarChartOptions).update();

    /*let data = [
      {
        "key":"Cabinet",
        "values":[
          { "axis": "light", "value": 0.0 },
          { "axis": "temperature", "value": 0.0 },
          { "axis": "humidity", "value": 0.0 }
        ]
      },
    ]
    this.radarChart.data(data).update();*/
  }
  componentDidUpdate(prevProps) {
    let data = [
      {
        "key":"Cabinet",
        "values":[
          { "axis": "light", "value": (this.props.data["light"]["median"] / 10000).toFixed(2) },
          { "axis": "temperature", "value": (this.props.data["temperature"]["median"] / 10000).toFixed(2) },
          { "axis": "humidity", "value": (this.props.data["humidity"]["median"] / 10000).toFixed(2) }
        ]
      },
    ];
    this.radarChart.data(data).update();
  }
  render() {
    const classString = `card card-width`;
    return (
      <div className={classString}>
        <div className="text-right mt-3">
          <div id={this.props.type}></div>
        </div>
        <div className="card-body">
          <h5 className="card-title">Radar</h5>
          <h6 className="card-subtitle mb-2 text-muted">
          </h6>
          <p className="card-text">
            This widget combines ambiance in the greenhouse.
          </p>
        </div>
      </div>
    );
  }
}
