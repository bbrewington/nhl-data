<!--
erDiagram key

Taken from: https://mermaid.js.org/syntax/entityRelationshipDiagram.html#relationship-syntax

Value (L)  Value (R)  Meaning
|o         o|         Zero or one
||         ||         Exactly one
}o         o{         Zero or more (no upper limit)
}|         |{         One or more (no upper limit)
-->

```mermaid
erDiagram
    Season ||--|{ Game : "has"
    Team ||--|{ PlayerTeamAssignment : "has"
    Player ||--|{ PlayerTeamAssignment : "assigned to"
    Season ||--|{ PlayerTeamAssignment : "during"
    Game ||--|| Team : "home team"
    Game ||--|| Team : "away team"
    %% Note on zero or more below: b/c have to web scrape these, it's likely there are missing entries
    Team ||--o{ GameProjectedLine : "publishes"
    Game ||--o{ GameProjectedLine : "has"
    Player ||--o{ GameProjectedLine : "is in"
    Game ||--|{ Play : "contains"
    Game ||--|{ ShiftChartEntry : "has"
    ShiftChartEntry ||--|| Player : "contains"
    Player ||--o{ Play : "makes"
    Play ||--o| Shot : "can be of type"
    Play ||--o| Goal : "can be of type"
    Play ||--o| Penalty : "can be of type"
    Goal ||--|| Player : "scored by"
    Goal ||--o{ Assist : "has"
    Assist ||--|| Player : "made by"
    Shot ||--|| Player : "taken by"
    Penalty ||--|| Player : "committed by"
    Game ||--o{ GoalieStats : "has"
    GoalieStats ||--|| Player : "for goalie"
```
