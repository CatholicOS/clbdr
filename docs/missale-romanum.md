# The Roman Missal — historical notes and edition line

*(Carried over from the absorbed CRMETDR repository.)*

The Roman Missal is the book containing the prescribed prayers, chants, and instructions for the celebration of Mass in the Roman Catholic Church. Published first in Latin under the title *Missale Romanum*, the text is then translated and, once approved by a recognitio by the Vatican [Dicastery for Divine Worship and the Discipline of the Sacraments](https://www.cultodivino.va/), is published in modern languages for use in local churches throughout the world.

In the earliest centuries of the Church, there were no books containing prescribed liturgical prayers, texts, or other instructions. Because the faith of the Church was (and still is) articulated in liturgical prayer, there was a need for consistency and authenticity in the words used in the celebration of the Liturgy. Collections of prayers developed gradually for use in particular locations and situations such as for a particular monastery, for the Pope, or for other local churches. Such collections were contained in *libelli* ("booklets") which over centuries were drawn together into larger collections of prayers.

Eventually larger, more organized collections of prayers were assembled into "sacramentaries" (*liber sacramentorum* or *sacramentarium*), which contained some, but not all, of the prayers of the Mass. The earliest of these sacramentaries were attributed to Pope Leo I, "Leo the Great" (440–461), and Pope Gelasius (492–496), but surviving versions of those sacramentaries date from centuries later. Other early manuscripts (such as the *Ordines Romani*) contained detailed descriptions of the celebration of the Mass with the Pope in Rome.

Those written accounts may have gradually served as instructions or rubrics for the celebration of Mass in other settings. Liturgical books grew as they passed from one community (a local church, a diocese, a monastery, etc.) to another, often with prayers added in margins or in blank spaces. The process of sharing text was by copying by hand — a laborious task which at times led to inconsistencies and errors.

The first true liturgical books which could be called "missals" were found in monasteries beginning around the 12th and 13th centuries. A *missale* contained not only the prayers but the biblical readings, the chants, and the rubrics for the celebration of Mass. It is difficult to trace the exact origins of the first missal.

Since that time, to accommodate the ongoing evolution and development of the Liturgy, new editions of the ***Missale Romanum*** were promulgated by Popes for use in the Church.

| Year | Status | Reigning Pope | Description |
|------|--------|---------------|-------------|
| 1474 | – | Sixtus IV | The first book bearing the name ***Missale Romanum***, published 34 years after Gutenberg's printing press. |
| 1570 | – | Pius V | Promulgated after the Council of Trent ([Quo primum](https://www.papalencyclicals.net/pius05/p5quopri.htm)), obligatory throughout the Latin Church except where another rite had been in place for at least 200 years. |
| 1604 | Editio typica | Clement VIII | |
| 1634 | Reimpressio emendata | Urban VIII | |
| 1884 | Reimpressio emendata | Leo XIII | |
| 1920 | Editio typica | Benedict XV | Incorporates revisions promulgated by Pius X. |
| 1957 | Reimpressio emendata | Pius XII | |
| 1962 | Editio typica | John XXIII | Incorporates the revised Code of Rubrics prepared by Pius XII's commission. |
| 1970 | Editio typica (prima) | Paul VI | Promulgated by the apostolic constitution [Missale Romanum](https://www.vatican.va/content/paul-vi/en/apost_constitutions/documents/hf_p-vi_apc_19690403_missale-romanum.html) (1969). |
| 1971 | Reimpressio emendata | Paul VI | |
| 1975 | Editio typica altera | Paul VI | |
| 2002 | Editio typica tertia | John Paul II | |
| 2008 | Reimpressio emendata | Benedict XVI | |

The full edition line, with canonical IDs (`missale_romanum_1474` … `missale_romanum_2008`) and short forms (`mr1474` … `mr2008`), is in [`data/editions.json`](../data/editions.json).

## Vernacular editions

Since the Second Vatican Council the liturgy is celebrated in the vernacular, with translations of the Roman Missal undertaken by Bishops' Conferences. These are identified as `<book>_<year>_<bcp47>`: the English edition published in the United States in 2011 is `missale_romanum_2011_en_US`; an eventual Spanish edition for the United States would be `missale_romanum_XXXX_es_US`.

Open use-case questions carried over for the committee:

- do the Spanish-speaking countries of Central / South America each publish their own language edition of the Roman Missal?
- does CELAM publish a single language edition, with each country / diocese adapting on a practical level when publishing the liturgical Ordo?
