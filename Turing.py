"""
Sistema de Máquinas de Turing para Cálculo de Fibonacci

Integrantes:   
            Oli Viau 23544
            Fabian Morales 23267


Historial de modificaciones:
        [000] 22/2/2026 programa nuevo
        [001] 23/2/2026 Definición turing
        [002] 25/2/2026 Convenciones completas
        [003] 26/2/2026 Testing
        [004] 27/2/2026 Modificaciones finales
"""

import json
import sys
import os

class TuringMachine:
    def __init__(self, config_file=None, num_tapes=3, tape_size=300):
        self.num_tapes = num_tapes
        self.tape_size = tape_size
        self.transitions = {}
        self.state = 'q0'
        self.accepting = []
        self.tapes = [['_'] * tape_size for _ in range(num_tapes)]
        self.heads = [tape_size // 2 for _ in range(num_tapes)]
        self.history = []
        if config_file:
            self.load_config(config_file)

    def load_config(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.transitions = {}
            for k, v in data['transitions'].items():
                state, symbols = k.split('|')
                sym_tuple = tuple(symbols.split(','))
                self.transitions[(state, sym_tuple)] = v

            self.state = data['initial_state']
            self.accepting = data['accepting_states']


    def load_input(self, tapes_content=None, head_positions=None):

        self.tapes = [['_'] * self.tape_size for _ in range(self.num_tapes)]
        self.heads = [self.tape_size // 2 for _ in range(self.num_tapes)]
        self.history = []

        if tapes_content:
            for t_index, content in enumerate(tapes_content):
                for i, char in enumerate(content):
                    self.tapes[t_index][self.heads[t_index] + i] = char

        if head_positions:
            self.heads = head_positions
    def log_step(self):
        step_info = f"Estado: {self.state}\n"
        for i in range(self.num_tapes):
            idx = self.heads[i]
       
            start = max(0, idx-15)
            end = min(len(self.tapes[i]), idx+16)
            slice_t = self.tapes[i][start:end]
            tape_str = "".join(slice_t)
            pointer_pos = min(15, idx)
            pointer = " " * pointer_pos + "^"
            step_info += f"  Cinta {i}: ...{tape_str}...\n           {pointer}\n"
        step_info += "-" * 60 + "\n"
        self.history.append(step_info)

    def step(self):
        current_syms = []
        for i in range(self.num_tapes):
            sym = self.get_symbol(i)
            current_syms.append(sym)
        current_syms = tuple(current_syms)

        self.log_step()

        # Búsqueda de transición exacta primero
        action = self.transitions.get((self.state, current_syms))

        if not action:
            # Búsqueda con comodines (*)
            candidates = [k for k in self.transitions if k[0] == self.state]
            for k in candidates:
                match = True
                target_syms = k[1]
                for i in range(self.num_tapes):
                    # * coincide con cualquier símbolo
                    if target_syms[i] != '*' and target_syms[i] != current_syms[i]:
                        match = False
                        break
                if match:
                    action = self.transitions[k]
                    break

        if action:
            self.state = action['next']
            writes = action['write']
            moves = action['move']
            for i in range(self.num_tapes):
                if writes[i] != '*':
                    self.get_symbol(i)
                    self.tapes[i][self.heads[i]] = writes[i]
                if moves[i] == 'R':
                    self.heads[i] += 1
                elif moves[i] == 'L':
                    self.heads[i] -= 1
            return True
        return False

    def run(self, max_steps=50000):
        steps = 0
        while self.state not in self.accepting and steps < max_steps:
            if not self.step():
                print(f"\nNo hay transición definida para estado '{self.state}' con símbolos: {tuple(self.tapes[i][self.heads[i]] for i in range(self.num_tapes))}")
                break
            steps += 1
        
        self.log_step()
        
        print(f"\nSimulación completada en {steps} pasos")
        print(f"Estado final: {self.state}")
        
        
        result = "".join(self.tapes[0]).strip('_')
        return result

    def export_derivations(self, filename="derivaciones.txt"):
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(self.history)
        print(f"Derivaciones guardadas en: {filename}")


    def get_symbol(self, tape_index):
        head = self.heads[tape_index]

        # Expandir a la derecha
        if head >= len(self.tapes[tape_index]):
            self.tapes[tape_index].extend(['_'] * 100)

        # Expandir a la izquierda
        if head < 0:
            self.tapes[tape_index] = ['_'] * 100 + self.tapes[tape_index]
            self.heads[tape_index] += 100
            head = self.heads[tape_index]

        return self.tapes[tape_index][head]

def main():
    print("PROYECTO 1: MÁQUINA DE TURING - FIBONACCI")

    #archivo de configuración
    config_file = input("\nIngrese el nombre del archivo JSON: ").strip()
    if not os.path.exists(config_file):
        print(f"Error: El archivo '{config_file}' no existe.")
        return

    #cadena de entrada
    input_string = input("Ingrese la cadena de entrada (ej: '111#' para F(3)): ").strip()

    print(f"\n Cargando configuración desde '{config_file}'...")
    tm = TuringMachine(config_file, num_tapes=3)

    print(f"Ejecutando simulación con entrada: '{input_string}'")
    ##
    ### BORRAR AL TERMINAR TESTING
    ##
   #tm.load_input([input_string])
    tm.load_input(["_", "111", "11"])
    result = tm.run()


    print(f"RESULTADO FINAL: {result}")
    print(f"Fibonacci de n={input_string.count('1')}: {result.count('1')} unos")

    # Exportar derivaciones
    deriv_file = "derivaciones_mt.txt"
    tm.export_derivations(deriv_file)



main()