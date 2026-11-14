# Fig. 2 saved dispatch

Run `python result_vis/plot_fig2.py` from the repository root. The script uses NumPy and Matplotlib and writes `figure/test/Fig2.pdf`. It does not import the core solver.

`plot_data.npz` contains the already selected trajectory and dispatch arrays. `provenance.json` records the training configuration and original evaluation scenario index. The single saved trajectory is original zero-based scenario 245, selected using sampling seed 10 from 5,000 scenarios.
