import React from "react";
import "./PlantForm.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faImage, faTimes, faCheck } from "@fortawesome/free-solid-svg-icons";
import Autosuggest from 'react-autosuggest';
import axios from "axios";

function renderInputComponent(inputProps) {
  return (
    <div>
      <input {...inputProps} /> {inputProps.remoteId ? <FontAwesomeIcon icon={faCheck} /> : ""} <span>selected id {inputProps.remoteId} value: {inputProps.remoteName}</span>
    </div>
  )
}


function escapeRegexCharacters(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
function getSuggestionValue(suggestion) {
  return suggestion.name
}
function getSuggestions(value, response) {
  const escapedValue = escapeRegexCharacters(value.trim());

  if (escapedValue === '') {
    return [];
  }

  const regex = new RegExp('\\b' + escapedValue, 'i');

  let suggestions = response.data.filter(plant => regex.test(getSuggestionValue(plant)));
  //return suggestions;
  return response.data;
}


function renderSuggestion(suggestion) {

  return (
    <div className="suggestion-content d-flex border-bottom">
      <div className="suggestion-image bg-light d-flex justify-content-center align-items-center">
        {suggestion.imageUrl ? <img src={suggestion.imageUrl} width="75" height="75" alt={suggestion.name} /> : <FontAwesomeIcon icon={faImage} size="2x" />}
      </div>
      <div className="d-flex flex-fill flex-column p-2">
        <h6 className="name">
          {suggestion.name}
        </h6>
        {suggestion.commonName ?
        <p className="common-name text-secondary m-0">
          {suggestion.commonName}
        </p>
        : ""}
      </div>
    </div>
  );
}

function debounce(func, wait) {
  let timeout;
  return function() {
    const context = this;
    const args = arguments;
    const later = function() {
      timeout = null;
      func.apply(context, args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export default class PlantForm extends React.Component {
  constructor() {
    super();

    this.state = {
      value: '',
      suggestions: [],
      isLoading: false,
      remoteId: null,
      remoteName: null,
    };
  }

  loadSuggestions = debounce((value) => {
    let self = this;
    axios.get(`/api/v1/shamrock/?q=${value}`).then(function(response) {
      self.setState({
        isLoading: false,
        suggestions: getSuggestions(value, response)
      });
    });
  }, 1000);

  onChange = (event, { newValue }) => {
    this.setState({
      value: newValue
    });
  };

  onSuggestionsFetchRequested = ({ value }) => {
    this.setState({
      isLoading: true
    });
    this.loadSuggestions(value);
  };

  onSuggestionsClearRequested = () => {
    this.setState({
      suggestions: [],
    });
  };

  onSuggestionSelected = (event, {suggestion}) => {
    this.setState({
      remoteId: suggestion.id,
      remoteName: suggestion.name,
    });
  };

  addPlant = (event) => {
    let payload = {remoteId: this.state.remoteId};
    this.props.createPlant(payload);
    this.props.toggle();
  }

  render() {
    const { value, suggestions, isLoading, remoteId, remoteName } = this.state;
    const inputProps = {
      placeholder: "Search plants:",
      value,
      remoteId,
      remoteName,
      onChange: this.onChange
    };
    return (
      <div className="custom-modal">
        <div className="obfuscator" onClick={this.props.toggle}></div>
        <div className="modal-dialog modal-lg">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">Add plant</h5>
              <button type="button" className="close" onClick={this.props.toggle}>
                <FontAwesomeIcon icon={faTimes} />
              </button>
            </div>
            <div className="modal-body">
              <p>Look for the plant in the remote database.</p>
              <form>
                <div className="form-group">
                  <label htmlFor="plant-name" className="col-form-label">Remote plant:</label>
                  <span className={isLoading ? "rounded-spinner" : ""}></span>
                  <Autosuggest
                    suggestions={suggestions}
                    onSuggestionsFetchRequested={this.onSuggestionsFetchRequested}
                    onSuggestionsClearRequested={this.onSuggestionsClearRequested}
                    onSuggestionSelected={this.onSuggestionSelected}
                    getSuggestionValue={getSuggestionValue}
                    renderSuggestion={renderSuggestion}
                    renderInputComponent={renderInputComponent}
                    inputProps={inputProps} />
                </div>
              </form>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={this.props.toggle}>Close</button>
              <button type="button" className="btn btn-primary" disabled={this.state.remoteId ? "" : true} onClick={this.addPlant}>Add plant</button>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
