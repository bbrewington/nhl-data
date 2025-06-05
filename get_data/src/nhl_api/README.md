# NHL API Client

## Reference Links

- API spec
  - https://github.com/Zmalski/NHL-API-Reference
  - https://gitlab.com/dword4/nhlapi
  
## Example API Responses

## Player.get_info

```python
{
    'playerId': 8478402,
    'isActive': True,
    'currentTeamId': 22,
    'currentTeamAbbrev': 'EDM',
    'fullTeamName': {'default': 'Edmonton Oilers', 'fr': "Oilers d'Edmonton"},
    'firstName': {'default': 'Connor'},
    'lastName': {'default': 'McDavid'},
    'teamLogo': 'https://assets.nhle.com/logos/nhl/svg/EDM_light.svg',
    'sweaterNumber': 97,
    'position': 'C',
    'headshot': 'https://assets.nhle.com/mugs/nhl/20232024/EDM/8478402.png',
    'heroImage': 'https://assets.nhle.com/mugs/actionshots/1296x729/8478402.jpg',
    'heightInInches': 73,
    'heightInCentimeters': 185,
    'weightInPounds': 194,
    'weightInKilograms': 88,
    'birthDate': '1997-01-13',
    'birthCity': {'default': 'Richmond Hill'},
    'birthStateProvince': {'default': 'Ontario'},
    'birthCountry': 'CAN',
    'shootsCatches': 'L',
    'draftDetails': {'year': 2015,
                    'teamAbbrev': 'EDM',
                    'round': 1,
                    'pickInRound': 1,
                    'overallPick': 1},
    'playerSlug': 'connor-mcdavid-8478402',
    'inTop100AllTime': 0,
    'inHHOF': 0,
    'featuredStats': {'season': 20232024, 'regularSeason': {...}},
    'careerTotals': {'regularSeason': {...}, 'playoffs': {...}},
    'shopLink': '#TODO',
    'twitterLink': '#TODO',
    'watchLink': '#TODO',
    'last5Games': [
        {   'assists': 4,
            'gameDate': '2024-03-21',
            'gameId': 2023021104,
            'gameTypeId': 2,
            'goals': 0,
            'homeRoadFlag': 'H',
            'opponentAbbrev': 'BUF',
            'pim': 0,
            'plusMinus': 2,
            'points': 4,
            'powerPlayGoals': 0,
            'shifts': 21,
            'shorthandedGoals': 0,
            'shots': 0,
            'teamAbbrev': 'EDM',
            'toi': '19:41'
        },
        ...
    ],
    'seasonTotals': [
        {
            'assists': 32,
            'avgToi': '18:53',
            'faceoffWinningPctg': 0.4123,
            'gameTypeId': 2,
            'gameWinningGoals': 5,
            'gamesPlayed': 45,
            'goals': 16,
            'leagueAbbrev': 'NHL',
            'otGoals': 1,
            'pim': 18,
            'plusMinus': -1,
            'points': 48,
            'powerPlayGoals': 3,
            'powerPlayPoints': 14,
            'season': 20152016,
            'sequence': 1,
            'shootingPctg': 0.1524,
            'shorthandedGoals': 0,
            'shorthandedPoints': 0,
            'shots': 105,
            'teamName': {'default': 'Edmonton Oilers',
                        'fr': "Oilers d'Edmonton"}
        },
        ...
    ],
    'awards': [
        {
            'trophy': {'default': 'Art Ross Trophy', 'fr': 'Trophée Art Ross'},
            'seasons': [{...}, ...]
        }
    ],
    'currentTeamRoster': [
        {
            'playerId': 8480803,
            'lastName': {'default': 'Bouchard'},
            'firstName': {'default': 'Evan'},
            'playerSlug': 'evan-bouchard-8480803'
        },
        ...
    ]
}
```

## Game.play_by_play

```python
{
  "id": 2023020204,
  "season": 20232024,
  "gameType": 2,
  "limitedScoring": False,
  "gameDate": "2023-11-10",
  "venue": {
    "default": "KeyBank Center"
  },
  "venueLocation": {
    "default": "Buffalo"
  },
  "startTimeUTC": "2023-11-11T00:00:00Z",
  "easternUTCOffset": "-05:00",
  "venueUTCOffset": "-05:00",
  "tvBroadcasts": [
    {
      "id": 284,
      "market": "N",
      "countryCode": "CA",
      "network": "SN1",
      "sequenceNumber": 22
    },
    ...
  ],
  "gameState": "OFF",
  "gameScheduleState": "OK",
  "periodDescriptor": {
    "number": 3,
    "periodType": "REG"
  },
  "awayTeam": {
    "id": 30,
    "name": {
      "default": "Wild"
    },
    "abbrev": "MIN",
    "score": 2,
    "sog": 35,
    "logo": "https://assets.nhle.com/logos/nhl/svg/MIN_light.svg",
    "placeName": {
      "default": "Minnesota"
    }
  },
  "homeTeam": {
    "id": 7,
    "name": {
      "default": "Sabres"
    },
    "abbrev": "BUF",
    "score": 3,
    "sog": 25,
    "logo": "https://assets.nhle.com/logos/nhl/svg/BUF_light.svg",
    "placeName": {
      "default": "Buffalo"
    }
  },
  "shootoutInUse": True,
  "otInUse": True,
  "clock": {
    "timeRemaining": "00:00",
    "secondsRemaining": 0,
    "running": False,
    "inIntermission": False
  },
  "displayPeriod": 1,
  "maxPeriods": 5,
  "gameOutcome": {
    "lastPeriodType": "REG"
  },
  "plays": [
    {
      "eventId": 102,
      "periodDescriptor": {
        "number": 1,
        "periodType": "REG"
      },
      "timeInPeriod": "00:00",
      "timeRemaining": "20:00",
      "situationCode": "1551",
      "homeTeamDefendingSide": "left",
      "typeCode": 520,
      "typeDescKey": "period-start",
      "sortOrder": 10
    },
    ...
  ],
  "rosterSpots": [
    {
      "teamId": 30,
      "playerId": 8470594,
      "firstName": {
        "default": "Marc-Andre"
      },
      "lastName": {
        "default": "Fleury"
      },
      "sweaterNumber": 29,
      "positionCode": "G",
      "headshot": "https://assets.nhle.com/mugs/nhl/20232024/MIN/8470594.png"
    },
    ...
  ],
  "gameVideo": {
    "threeMinRecap": 6340913541112,
    "condensedGame": 6340912767112
  },
  "regPeriods": 3,
  "summary": {
    "teamGameStats": [
      {
        "category": "sog",
        "awayValue": 35,
        "homeValue": 25
      },
      {
        "category": "faceoffWinningPctg",
        "awayValue": 0.727273,
        "homeValue": 0.272727
      },
      {
        "category": "powerPlay",
        "awayValue": "2/5",
        "homeValue": "0/4"
      },
      {
        "category": "powerPlayPctg",
        "awayValue": 0.4,
        "homeValue": 0
      },
      {
        "category": "pim",
        "awayValue": 8,
        "homeValue": 10
      },
      {
        "category": "hits",
        "awayValue": 31,
        "homeValue": 20
      },
      {
        "category": "blockedShots",
        "awayValue": 18,
        "homeValue": 22
      },
      {
        "category": "giveaways",
        "awayValue": 6,
        "homeValue": 6
      },
      {
        "category": "takeaways",
        "awayValue": 6,
        "homeValue": 2
      }
    ],
    "seasonSeries": [
      {
        "id": 2023020204,
        "season": 20232024,
        "gameType": 2,
        "gameDate": "2023-11-10",
        "startTimeUTC": "2023-11-11T00:00:00Z",
        "easternUTCOffset": "-05:00",
        "venueUTCOffset": "-05:00",
        "gameState": "OFF",
        "gameScheduleState": "OK",
        "awayTeam": {
          "id": 30,
          "abbrev": "MIN",
          "logo": "https://assets.nhle.com/logos/nhl/svg/MIN_light.svg",
          "score": 2
        },
        "homeTeam": {
          "id": 7,
          "abbrev": "BUF",
          "logo": "https://assets.nhle.com/logos/nhl/svg/BUF_light.svg",
          "score": 3
        },
        "clock": {
          "timeRemaining": "00:00",
          "secondsRemaining": 0,
          "running": False,
          "inIntermission": False
        },
        "gameCenterLink": "/gamecenter/min-vs-buf/2023/11/10/2023020204",
        "periodDescriptor": {
          "number": 3,
          "periodType": "REG"
        },
        "gameOutcome": {
          "lastPeriodType": "REG"
        }
      },
      ...
    ],
    "seasonSeriesWins": {
      "awayTeamWins": 0,
      "homeTeamWins": 2
    },
    "linescore": {
      "byPeriod": [
        {
          "periodDescriptor": {
            "number": 1,
            "periodType": "REG"
          },
          "away": 1,
          "home": 1
        },
        {
          "periodDescriptor": {
            "number": 2,
            "periodType": "REG"
          },
          "away": 0,
          "home": 1
        },
        {
          "periodDescriptor": {
            "number": 3,
            "periodType": "REG"
          },
          "away": 1,
          "home": 1
        }
      ],
      "totals": {
        "away": 2,
        "home": 3
      }
    },
    "shotsByPeriod": [
      {
        "periodDescriptor": {
          "number": 1,
          "periodType": "REG"
        },
        "away": 10,
        "home": 11
      },
      ...
    ],
    "gameReports": {
      "gameSummary": "https://www.nhl.com/scores/htmlreports/20232024/GS020204.HTM",
      "eventSummary": "https://www.nhl.com/scores/htmlreports/20232024/ES020204.HTM",
      "playByPlay": "https://www.nhl.com/scores/htmlreports/20232024/PL020204.HTM",
      "faceoffSummary": "https://www.nhl.com/scores/htmlreports/20232024/FS020204.HTM",
      "faceoffComparison": "https://www.nhl.com/scores/htmlreports/20232024/FC020204.HTM",
      "rosters": "https://www.nhl.com/scores/htmlreports/20232024/RO020204.HTM",
      "shotSummary": "https://www.nhl.com/scores/htmlreports/20232024/SS020204.HTM",
      "shiftChart": "https://www.nhl.com/stats/shiftcharts?id=2023020204",
      "toiAway": "https://www.nhl.com/scores/htmlreports/20232024/TV020204.HTM",
      "toiHome": "https://www.nhl.com/scores/htmlreports/20232024/TH020204.HTM"
    },
    "gameInfo": {
      "referees": [{"default": "Jon McIsaac"}, {"default": "Wes McCauley"}],
      "linesmen": [{"default": "James Tobias"}, {"default": "Brandon Grillo"}],
      "awayTeam": {
        "headCoach": {
          "default": "Dean Evason"
        },
        "scratches": [
          {
            "id": 8475750,
            "firstName": {
              "default": "Jon"
            },
            "lastName": {
              "default": "Merrill"
            }
          },
          ...
        ]
      },
      "homeTeam": {
        "headCoach": {
          "default": "Don Granato"
        },
        "scratches": [
          {
            "id": 8477949,
            "firstName": {
              "default": "Alex"
            },
            "lastName": {
              "default": "Tuch"
            }
          },
          ...
        ]
      }
    }
  }
}
```