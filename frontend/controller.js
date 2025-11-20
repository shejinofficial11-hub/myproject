$(document).ready(function () {
  // Display Speak Message
  eel.expose(DisplayMessage);
  function DisplayMessage(message) {
    $(".siri-message li:first").text(message);
    $(".siri-message").textillate("start");
  }

  eel.expose(ShowHood);
  function ShowHood() {
    $("#Oval").attr("hidden", false);
    $("#SiriWave").attr("hidden", true);
  }

  eel.expose(senderText);
  function senderText(message) {
    var chatBox = document.getElementById("chat-canvas-body");
    if (message.trim() !== "") {
      chatBox.innerHTML += `<div class="row justify-content-end mb-4">
          <div class = "width-size">
          <div class="sender_message">${message}</div>
      </div>`;

      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  eel.expose(receiverText);
  function receiverText(message) {
    var chatBox = document.getElementById("chat-canvas-body");
    if (message.trim() !== "") {
      chatBox.innerHTML += `<div class="row justify-content-start mb-4">
          <div class = "width-size">
          <div class="receiver_message">${message}</div>
          </div>
      </div>`;

      // Scroll to the bottom of the chat box
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }
  eel.expose(hideLoader);
  function hideLoader() {
    $("#Loader").attr("hidden", true);
    $("#FaceAuth").attr("hidden", false);
  }
  // Hide Face auth and display Face Auth success animation
  eel.expose(hideFaceAuth);
  function hideFaceAuth() {
    $("#FaceAuth").attr("hidden", true);
    $("#FaceAuthSuccess").attr("hidden", false);
  }
  // Hide success and display
  eel.expose(hideFaceAuthSuccess);
  function hideFaceAuthSuccess() {
    $("#FaceAuthSuccess").attr("hidden", true);
    $("#HelloGreet").attr("hidden", false);
  }

  // Hide Start Page and display blob
  eel.expose(hideStart);
  function hideStart() {
    $("#Start").attr("hidden", true);

    setTimeout(function () {
      $("#Oval").addClass("animate__animated animate__zoomIn");
    }, 1000);
    setTimeout(function () {
      $("#Oval").attr("hidden", false);
    }, 1000);
  }

  // Weather Display Functions
  eel.expose(displayWeather);
  function displayWeather(weatherData) {
    if (weatherData && weatherData.current) {
      const weather = weatherData.current;
      const weatherHtml = `
        <div class="weather-widget">
          <h5>Weather in ${weather.location}</h5>
          <p>${weather.temperature}°C - ${weather.description}</p>
          <small>Humidity: ${weather.humidity}% | Wind: ${weather.wind_speed} m/s</small>
        </div>
      `;

      // Display weather in chat
      var chatBox = document.getElementById("chat-canvas-body");
      chatBox.innerHTML += `<div class="row justify-content-start mb-4">
        <div class="width-size">
          <div class="receiver_message">${weatherHtml}</div>
        </div>
      </div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  // Calendar Display Functions
  eel.expose(displayCalendarEvents);
  function displayCalendarEvents(eventData) {
    if (eventData && eventData.events) {
      const events = eventData.events;
      let eventsHtml = '<div class="calendar-widget"><h5>Your Schedule</h5>';

      if (events.length === 0) {
        eventsHtml += '<p>No events scheduled</p>';
      } else {
        eventsHtml += '<ul class="event-list">';
        events.forEach(event => {
          eventsHtml += `<li><strong>${event.time}</strong> - ${event.title}</li>`;
        });
        eventsHtml += '</ul>';
      }

      eventsHtml += '</div>';

      // Display events in chat
      var chatBox = document.getElementById("chat-canvas-body");
      chatBox.innerHTML += `<div class="row justify-content-start mb-4">
        <div class="width-size">
          <div class="receiver_message">${eventsHtml}</div>
        </div>
      </div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  // Notes Display Functions
  eel.expose(displayNotes);
  function displayNotes(notesData) {
    if (notesData && notesData.notes) {
      const notes = notesData.notes;
      let notesHtml = '<div class="notes-widget"><h5>Your Notes</h5>';

      if (notes.length === 0) {
        notesHtml += '<p>No notes found</p>';
      } else {
        notesHtml += '<ul class="notes-list">';
        notes.forEach(note => {
          notesHtml += `<li><em>[${note.category}]</em> - ${note.content}</li>`;
        });
        notesHtml += '</ul>';
      }

      notesHtml += '</div>';

      // Display notes in chat
      var chatBox = document.getElementById("chat-canvas-body");
      chatBox.innerHTML += `<div class="row justify-content-start mb-4">
        <div class="width-size">
          <div class="receiver_message">${notesHtml}</div>
        </div>
      </div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  // Quick Action Buttons
  function addQuickActionButtons() {
    const quickActionsHtml = `
      <div class="quick-actions">
        <button onclick="getWeatherInfo()" class="btn btn-sm btn-info mr-2">🌤️ Weather</button>
        <button onclick="getTodaySchedule()" class="btn btn-sm btn-warning mr-2">📅 Schedule</button>
        <button onclick="getRecentNotes()" class="btn btn-sm btn-success mr-2">📝 Notes</button>
      </div>
    `;

    // Add quick actions to the interface if they don't exist
    if ($("#quick-actions-container").length === 0) {
      $("#chat-canvas-body").after(`
        <div id="quick-actions-container" class="quick-actions-container mb-3">
          ${quickActionsHtml}
        </div>
      `);
    }
  }

  // Quick action functions
  function getWeatherInfo() {
    eel.getWeather()(function(weatherData) {
      // Weather will be displayed through displayWeather function
    });
  }

  function getTodaySchedule() {
    eel.getTodayEvents()(function(eventData) {
      // Events will be displayed through displayCalendarEvents function
    });
  }

  function getRecentNotes() {
    eel.getRecentNotes(5)();
  }

  // Initialize quick actions when document is ready
  setTimeout(function() {
    addQuickActionButtons();
  }, 2000);

});
