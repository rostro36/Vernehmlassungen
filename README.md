# Vernehmlassungen scraping and analysing
## Purpose
This project tries to find the answer how long it takes for a motion to come into effect in a law. The process is outlined in an official article on [ch.ch](https://www.ch.ch/de/politisches-system/volkerrecht/wie-entsteht-ein-gesetz/).

## Data acquisition
The first sign of a motion to make a law I found was the *Vernehmlassung*, the process of researching possible effects of the law and discussion with different stakeholders. These *Vernehmlassungen* are listed on the [official website of the Swiss Law](https://www.fedlex.admin.ch/de/consultation-procedures).

There is no direct link or reference between a *Vernehmlassung* and a new law, so an approximation had to be made. Many (newer) *Vernehmlassungen* list the laws they may change. So, the most optimistic value was chosen, being the earliest listed change date, where the vote and change date are after the end of the *Vernehmlassung*. If there are multiple laws listed, the mode of the accept date was considered and the average of the vote date with the selected mode was used.

This approximation is too optimistic in assuming that each *Vernehmlassung* was discussed as soon as possible and more importantly the adjacent change in law was also accepted. On the other hand, even if that particular change in law was rejected, the *Vernehmlassung* was still read and used for the following processes and laws.

## Plots
In the folder [plots](./plots) there are many plots contained which visualize some of the key features and can be used to answer some important questions.

**Vernehmlassungen per year**

![Vernehmlassung Year Plot](https://github.com/rostro36/Vernehmlassungen/blob/master/plots/Vernehmlassung%20Year.svg)

**Vernehmlassungen per department and avg/median time to law**
![Department Plot](./plots/Department.svg)

## ToDo
- Refactoring of code
- Machine Learning model
	- Without text
	- With text
- List libraries etc.
