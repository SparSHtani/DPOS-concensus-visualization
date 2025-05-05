from flask import Flask, render_template, request
import time
import threading

app = Flask(__name__)

nodes = [
    {"id": 1, "stake": 0, "is_delegate": False, "message": "", "vote": ""},
    {"id": 2, "stake": 0, "is_delegate": False, "message": "", "vote": ""},
    {"id": 3, "stake": 0, "is_delegate": False, "message": "", "vote": ""},
    {"id": 4, "stake": 0, "is_delegate": False, "message": "", "vote": ""},
]

proposed_node = None
vote_result = None

@app.route('/')
def index():
    return render_template('index.html', nodes=nodes, proposed_node=proposed_node, vote_result=vote_result)

@app.route('/submit_stake', methods=['POST'])
def submit_stake():
    global proposed_node, vote_result
    vote_result = None  # Reset previous result

    for node in nodes:
        stake_input = request.form.get(f'stake{node["id"]}')
        node['stake'] = int(stake_input) if stake_input else 0
        node['message'] = ""
        node['is_delegate'] = False
        node['vote'] = ""

    # Pick top 2 stakeholders as delegates
    sorted_nodes = sorted(nodes, key=lambda x: x['stake'], reverse=True)
    top_delegates = sorted_nodes[:2]
    for d in top_delegates:
        d['is_delegate'] = True

    proposed_node = max(top_delegates, key=lambda x: x['stake'])

    # Simulate counting task
    def count_and_propose():
        proposed_node['message'] = "Starting block proposal..."
        for i in range(0, 501, max(1, proposed_node['stake'])):
            proposed_node['message'] = f"Counting... {i}"
            time.sleep(0.1)
        proposed_node['message'] = f"Node {proposed_node['id']} proposes a block!"

    threading.Thread(target=count_and_propose).start()

    return render_template('index.html', nodes=nodes, proposed_node=proposed_node, vote_result=vote_result)

@app.route('/vote', methods=['POST'])
def vote():
    global vote_result

    yes_votes = 0
    no_votes = 0

    for node in nodes:
        if node['is_delegate']:
            node['vote'] = request.form.get(f'vote{node["id"]}')
            if node['vote'] == "Yes":
                yes_votes += 1
            elif node['vote'] == "No":
                no_votes += 1
        else:
            node['vote'] = ""  # Clear any accidental input from non-delegates

    if yes_votes > no_votes:
        vote_result = f"✅ Block accepted by majority vote of delegates ({yes_votes} Yes / {no_votes} No)."
    else:
        vote_result = f"❌ Block rejected by majority vote of delegates ({yes_votes} Yes / {no_votes} No)."

    return render_template('index.html', nodes=nodes, proposed_node=proposed_node, vote_result=vote_result)

if __name__ == '__main__':
    app.run(debug=True)
