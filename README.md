

# Use Case Orchestration with Miro Integration

This project orchestrates use case exploration and visualization by integrating with the [Miro REST API](https://developers.miro.com/reference/overview). It processes a use case database (Excel file) and programmatically creates elements (sticky notes, shapes) and connectors on a Miro board.

## Features

- Reads use case data from an Excel template.
- Automatically creates sticky notes or shapes for each use case on a Miro board.
- Positions notes in the space impact vs effort (calculated via functionality of this package).
- Colors notes by project (can be defined).
- Adds connectors between use cases based on solution subcategories (or any other entry).
- Uses the official [Miro REST API](https://developers.miro.com/reference/overview).

## Setup

1. **Clone the repository** and install dependencies:
	 ```bash
	 pip install -e .
	 ```

2. **Set up environment variables** for Miro API access:
	 - Obtain your `ACCESS_TOKEN` and `BOARD_ID` from your Miro account.
	 - Export them in your shell:
		 ```bash
		 export ACCESS_TOKEN=your_miro_access_token
		 export BOARD_ID=your_miro_board_id
		 source scripts/env.sh  # (if you use the provided env.sh)
		 ```

3. **Check your connection to Miro:**
	 ```python
	 from useCaseOrch import miro
	 miro.check_connection()
	 ```

## Running the Script

- The main script is at `scripts/script.py`.
- It expects the Excel file `Use case collection template.xlsx` in the project root.
- To run:
	```bash
	python scripts/script.py
	```
- The script will:
	- Read and preprocess the Excel file into a pandas DataFrame.
	- Create sticky notes (or shapes) for each use case on your Miro board.
	- Add connectors between related use cases.

## Customization

- You can adjust the input (Excel) file, pre-processing of the data, color schemes, and scaling in `scripts/script.py`.
- For more on the Miro API, see the [Miro REST API documentation](https://developers.miro.com/reference/overview).

## Troubleshooting

- Ensure your `ACCESS_TOKEN` is valid and not expired.
- If you see authentication errors, re-generate your token and re-export it.
- Check the console output for error messages from the Miro API.


