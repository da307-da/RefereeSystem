// New functionality for real-time fixture updates
// Poll function to update fixtures regularly
  function updateFixtures() {
    fetch('/api/match_details_api/')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          updateLiveMatches(data.live_matches);
          updateGameweekMatches(data.past_matches);
        }
      })
      .catch(error => {
        console.error('Error fetching fixture updates:', error);
      });
  }
  
  // Update live matches in the DOM
  function updateLiveMatches(matches) {
    const container = document.querySelector('.live-matches ul');
    if (!container) return;
    
    if (matches.length === 0) {
      container.innerHTML = `
        <p style="
          font-size: 13px;
          color: #64748b;
          text-align: center;
          font-style: italic;
          padding: 12px;
          background-color: #f8fafc;
          border-radius: 6px;
        ">No live matches at the moment</p>
      `;
      return;
    }
    
    let html = '';
    matches.forEach(match => {
      html += `
        <li class="match-item" style="
          background-color: #f8fafc;
          border-radius: 6px;
          padding: 12px;
          margin-bottom: 8px;
          border-left: 3px solid #e53e3e;
        ">
          <div class="match-teams" style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
          ">
            <div class="team home" style="
              font-weight: 500;
              text-align: left;
              width: 40%;
            ">${match.teams.home.name}</div>
            
            <div class="score" style="
              font-weight: 700;
              font-size: 16px;
              text-align: center;
              width: 20%;
            ">${match.goals.home} - ${match.goals.away}</div>
            
            <div class="team away" style="
              font-weight: 500;
              text-align: right;
              width: 40%;
            ">${match.teams.away.name}</div>
          </div>
          
          <div class="match-status" style="
            font-size: 12px;
            color: #e53e3e;
            text-align: center;
          ">${match.fixture.status.elapsed}' | ${match.fixture.status.long}</div>
        </li>
      `;
    });
    
    container.innerHTML = html;
  }
  
  // Update gameweek matches in the DOM
  function updateGameweekMatches(matches) {
    const container = document.querySelector('.gameweek-matches ul');
    if (!container) return;
    
    if (matches.length === 0) {
      container.innerHTML = `
        <p style="
          font-size: 13px;
          color: #64748b;
          text-align: center;
          font-style: italic;
          padding: 12px;
          background-color: #f8fafc;
          border-radius: 6px;
        ">No match data available</p>
      `;
      return;
    }
    
    let html = '';
    matches.slice(0, 10).forEach(match => {
      const matchDate = new Date(match.fixture.date);
      const formattedDate = matchDate.toLocaleDateString('en-GB', { 
        weekday: 'short',
        day: 'numeric', 
        month: 'short', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).replace(',', ' -');
      
      html += `
        <li class="match-item" style="
          background-color: #f8fafc;
          border-radius: 6px;
          padding: 12px;
          margin-bottom: 8px;
          border-left: 3px solid #4299e1;
        ">
          <div class="match-date" style="
            font-size: 11px;
            color: #718096;
            margin-bottom: 6px;
          ">${formattedDate}</div>
          
          <div class="match-teams" style="
            display: flex;
            justify-content: space-between;
            align-items: center;
          ">
            <div class="team home" style="
              font-weight: 500;
              text-align: left;
              width: 40%;
            ">${match.teams.home.name}</div>
            
            <div class="score" style="
              font-weight: 700;
              font-size: 16px;
              text-align: center;
              width: 20%;
            ">${match.goals.home} - ${match.goals.away}</div>
            
            <div class="team away" style="
              font-weight: 500;
              text-align: right;
              width: 40%;
            ">${match.teams.away.name}</div>
          </div>
          
          <div class="match-status" style="
            font-size: 11px;
            color: #718096;
            text-align: center;
            margin-top: 6px;
          ">${match.fixture.status.long}</div>
        </li>
      `;
    });
    
//    container.innerHTML = html;
  }
  
  // Set up a polling interval for updates
//  document.addEventListener('DOMContentLoaded', () => {
    // Don't call updateFixtures() immediately if you want to wait for the first interval
    // updateFixtures();
    
    // Update every 60 seconds
//    setInterval(updateFixtures, 60000);
//  });