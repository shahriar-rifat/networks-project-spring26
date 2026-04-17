# Analysis

Run context: April 16, 2026 from Boston, MA (`42.3584, -71.0598`).

Measured inefficiency ratios from this run:

| City | Median RTT (ms) | Theoretical Min RTT (ms) | Inefficiency Ratio |
|------|-----------------:|-------------------------:|-------------------:|
| London | 372.0 | 52.6 | 7.07 |
| Frankfurt | 548.5 | 59.0 | 9.30 |
| Sao Paulo | 555.3 | 77.5 | 7.17 |
| Lagos | 550.2 | 82.4 | 6.68 |
| Tokyo | 374.8 | 107.9 | 3.47 |
| Mumbai | 553.9 | 122.5 | 4.52 |
| Singapore | 551.3 | 151.3 | 3.64 |
| Sydney | 557.6 | 162.4 | 3.43 |

## 1. Highest inefficiency ratio

Frankfurt had the highest inefficiency ratio in my measurements: `548.5 / 59.0 = 9.30x`.

A likely reason is that Frankfurt is not itself a submarine cable landing point[1]. Instead, it functions as a major inland Internet hub centered around DE-CIX Frankfurt, which DE-CIX describes as the world’s leading Internet Exchange [2]. As a result, traffic from Boston must first cross the Atlantic to a coastal landing point in Europe or the UK and then continue over terrestrial fiber into Frankfurt [3]. For example, the Atlantic Crossing-1 system lands in the UK, the Netherlands, Germany, and the United States, illustrating that transatlantic traffic typically reaches coastal landing stations before being carried inland [3].

This helps explain why Frankfurt appears less efficient than London. The extra inland backhaul, together with routing policies based on peering and congestion rather than pure geographic shortest path, can increase RTT beyond the simple Boston to Frankfurt great-circle baseline [2][3]. Therefore, the high ratio does not necessarily indicate weak infrastructure in Frankfurt. Instead, it reflects the fact that Frankfurt is a major inland exchange hub served through coastal cable landings and terrestrial backhaul [2][3].

## References

[1] submarinecablemap.com
[2] DE-CIX Frankfurt, “Connect to the world’s leading IX.”
[3] TeleGeography, Submarine Cable Map, including Atlantic Crossing-1 landing points.

## 2. Closest to the theoretical minimum

Sydney is the closest to the theoretical minimum `3.43x` in this experiment, with Tokyo only slightly behind `3.47x`. Although Sydney is much farther from Boston than most of the other cities, its measured RTT is relatively efficient compared to its great-circle distance. This indicates that the end-to-end route likely followed a fairly direct and well-provisioned long-haul path.

A low inefficiency ratio usually suggests strong backbone connectivity, good interconnection between major providers, and limited unnecessary detours. In other words, the path may still be long, but it is being carried efficiently over major international links rather than through excessive routing overhead. This is consistent with the broader Asia-Pacific infrastructure environment, where cities such as Tokyo are supported by dense trans-Pacific cable systems and major exchange ecosystems.

Therefore, Sydney’s low ratio does not mean it is geographically close. Instead, it shows that the routing infrastructure serving that path is relatively efficient for such a long-distance connection.

## 3. Why Lagos Likely Routes Through Europe First

A likely explanation for the Lagos result is that African Internet traffic has historically been structured in a way that sends a significant amount of traffic through Europe before reaching its final destination. This pattern is often called **tromboning**, where traffic takes an indirect international path instead of staying within the region [1][2].

There are several reasons for this. First, many of the earliest major international cable systems connecting African countries were designed primarily to link Africa with Europe rather than to create dense direct connectivity between African networks [1]. Second, Europe developed stronger peering ecosystems, larger Internet exchange points, and broader content hosting capacity much earlier than most African regions. As a result, cities such as London, Amsterdam, Paris, and Frankfurt became natural relay points for international traffic [2][3]. Third, even where submarine cables land in African countries, this does not automatically ensure strong regional routing. Efficient regional connectivity also depends on cross-border terrestrial fiber, carrier-neutral facilities, and widespread peering among operators, all of which remain uneven across the continent [2][3].

To improve this situation, Africa would need stronger regional interconnection rather than only additional submarine cable capacity. This includes greater peering at African IXPs, more carrier-neutral data centers, more local content caching and cloud deployment, and stronger east-west and north-south terrestrial fiber across the continent [2][3]. These changes would allow more traffic to remain within Africa instead of being routed through Europe first.

Lagos itself is now connected to several major cable systems, including **2Africa, ACE, Equiano, Glo-1, MainOne, NCSCS, SAT-3/WASC, and WACS** [1]. This suggests that the main limitation is no longer simple cable access. Instead, the larger issue is how networks interconnect regionally and where content and services are hosted. Therefore, Africa routes through Europe not because it lacks submarine cables altogether, but because the broader peering, hosting, and traffic-exchange ecosystem is still heavily Europe-centered [1][2][3].

## References

[1] TeleGeography, *Submarine Cable Map*, Lagos landing point.  
[2] Internet Society, “Internet Exchange Points (IXPs).”  
[3] Internet Society, *Anchoring the African Internet Ecosystem: Lessons from Kenya and Nigeria*.  
