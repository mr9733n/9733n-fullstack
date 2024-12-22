from flask import render_template, request
import numpy as np

config = {
    'first_number': 1,
    'last_number': 18,
    'numbers_to_select': 3,
    'simulation_runs': 10000000
}

def run_simulation(config):
    total_runs = config['simulation_runs']
    all_numbers = np.arange(config['first_number'], config['last_number'] + 1)
    results = np.random.choice(all_numbers, size=(total_runs, config['numbers_to_select'])).flatten()
    return results

def analyze_results(results, config):
    total_runs = config['simulation_runs']
    unique, counts = np.unique(results, return_counts=True)
    frequencies = counts / (total_runs * config['numbers_to_select']) * 100
   
    analysis = {
        'frequency': dict(zip(unique, frequencies)),
        'top': unique[np.argsort(-counts)[:config['numbers_to_select']]],
        'missing_numbers': [number for number in range(config['first_number'], config['last_number'] + 1) if number not in unique]
    }

    return analysis

def top_analyze(version):
    default_first_number = config['first_number']
    default_last_number = config['last_number']
    default_numbers_to_select = config['numbers_to_select']
    default_simulation_runs = config['simulation_runs']
    
    if request.method == 'POST':
        user_input = {}
        
        user_input['first_number'] = int(request.form.get('first_number', default_first_number))
        user_input['last_number'] = int(request.form.get('last_number', default_last_number))
        user_input['numbers_to_select'] = int(request.form.get('numbers_to_select', default_numbers_to_select))
        user_input['simulation_runs'] = int(request.form.get('simulation_runs', default_simulation_runs))
        
        results = run_simulation(user_input)
        analysis = analyze_results(results, user_input)  
        
        return render_template('random_top_analyze.html', analysis=analysis, 
                               version=version,
                               default_first_number=user_input['first_number'], 
                               default_last_number=user_input['last_number'], 
                               default_numbers_to_select=user_input['numbers_to_select'], 
                               default_simulation_runs=user_input['simulation_runs'])
    
    return render_template('random_top_analyze.html', 
                           version = version,
                           default_first_number=default_first_number, 
                           default_last_number=default_last_number, 
                           default_numbers_to_select=default_numbers_to_select, 
                           default_simulation_runs=default_simulation_runs)
