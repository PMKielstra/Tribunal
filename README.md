# Tribunal

Sort anything that humans can compare pairwise: applicants, proposals, stories, anything that fits in a CSV file.  Seamless drop-in/drop-out allows multiple people to collaborate on the sorting process as and when their individual schedules allow.  An upper limit on the number of entries to accept makes sorting even faster, avoiding wasting time comparing the 25th-best to the 26th when you've already determined you won't take more than the top twelve.  Especially good entries can be unilaterally accepted, skipping the sorting process altogether, while especially bad ones can be unilaterally dropped.

## Security Warning

Saving and loading state are accomplished through unauthenticated pickles.  If an attacker can start a Tribunal instance, they can use it to execute arbitrary code.

In general, Tribunal has no protections against malicious actors.  Anyone, with any motive, can join or leave the sorting process as and when they like as long as they can access the IP and port where it's running.

## Installation and Usage

```bash
pip install -r requirements.txt
cd src
flask run
```

Tribunal instances go through three phases:

1. Data input.  Any user may upload a CSV file.

2. Sorting.  Once a file has been uploaded, all users are now given two rows from the file and invited to choose one as ranked higher than the other -- or to accept or reject one entirely.

3. Output.  When the final comparison is completed, all users are shown a page listing all accepted entries.  The explicitly accepted ones come first, followed by those from the top of the list in sorted order.  Users may also download the ranked results as a CSV, which will include a new column giving the position of each line in the original CSV.  (This is 1-indexed.)

During the sorting phase, users may also download a pickle ("Tribunal save file") of the instance's internal state.  If they are forced to shut down their current instance, they may upload this to a new one and pick up where they left off.

In the output phase, entries are identified to users by their first-column entries.  For maximum readability, make sure that this is human-readable and not a timestamp or a unique ID.

There is no way to leave the output phase.  To sort a new dataset, start a new instance.
