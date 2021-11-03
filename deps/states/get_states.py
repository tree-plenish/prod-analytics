def get_states(state_column):
    
    # Libs, annoying. Don't iterate me pls.
    import numpy as np
    import pandas as pd

    # Loading in and cleaning states/abbrevs/code lookup table
    states = pd.read_csv("./deps/states/states.csv")
    states["State"] = [state.lower() for state in states["State"]]
    states["Abbrev"] = [abb.replace(".","").lower() for abb in states["Abbrev"]]
    states["Code"] = [code.lower() for code in states["Code"]]

    # Getting distribution of how people describe state
    state_input = {"state":0,"abbrev":0,"code":0,"unident":0}
    state_user = [state.lower() for state in state_column]
    state_idx = []

    # Looping through user states to get aquisition type counts and global labels
    for state in state_user:
        
        if state in states["State"].values:
            state_input["state"] = state_input["state"] + 1
            idx = np.argmax(states["State"] == state)
        elif state in states["Abbrev"].values:
            state_input["abbrev"] = state_input["abbrev"] + 1
            idx = np.argmax(states["Abbrev"] == state)
        elif state in states["Code"].values:
            state_input["code"] = state_input["code"] + 1
            idx = np.argmax(states["Code"] == state)
        else:
            state_input["unident"] = state_input["unident"] + 1
            idx = 999
        state_idx.append(idx)
        
    # Displaying identification status
    print("ID Status: ", state_input)

    # Getting state code from state index
    state_codes = [states["Code"].values[i] if i!=999 else "UNKNOWN" for i in state_idx]
    
    return state_codes