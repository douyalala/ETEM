from .toolkit import findClassNo

class Log:
    def __init__(self, file_name, pos_list=[], actions=[]):
        self.logfile = open(file_name, 'w')
        self.pos_list = pos_list
        self.actions = actions
    
    def record_line(self, line):
        self.logfile.write(f'{line}\n')
        self.logfile.flush()
    
    def record_new_mut(self, commandMutate):
        self.logfile.write('----------\n')
        self.logfile.write(f'mutation rule: {commandMutate}\n')
        self.logfile.flush()
    
    def record_mut_pos(self, mutate_pos, mut_cmd_line):
        self.logfile.write(f'mutate pos: {mutate_pos}\n')
        self.logfile.write(f'mutate cmd: {mut_cmd_line}\n')
        self.logfile.flush()
    
    def record_stat_before_mut(self, pos_ind_available, actionNo, mutator_available_in_class):
        self.logfile.write(f'pos_left_this_mutator: [{len(pos_ind_available[actionNo])}] {[ self.pos_list[ind] for ind in pos_ind_available[actionNo] ]}\n')
        self.logfile.write(f'mutator_left_this_class: [{len(mutator_available_in_class[findClassNo(actionNo)])}] {[ self.actions[mut] for mut in mutator_available_in_class[findClassNo(actionNo)] ]}\n')
        self.logfile.write(f'pos_left_each_mutator: [{sum(len(s) for s in pos_ind_available)}] {[ (self.actions[i], [self.pos_list[ind] for ind in pset]) for i,pset in enumerate(pos_ind_available) if len(pset) > 0 ]}\n')
        self.logfile.write(f'mutator_left_each_class: [{sum(len(s) for s in mutator_available_in_class)}] { [ [ self.actions[mut] for mut in mset] for mset in mutator_available_in_class if len(mset)>0 ] }\n')
        self.logfile.flush()
    
    def record_time(self, event, endtime):
        self.logfile.write(f'{event}-Time: {endtime}\n')
        self.logfile.flush()
    
    def record_false(self, why_false, endtime):
        self.logfile.write(f'succeed? False\n')
        self.logfile.write(f'Why not: {why_false}\n')
        self.logfile.write(f'EndTime: {endtime}\n')
        self.logfile.flush()
    
    def record_true(self, instantReward, endtime):
        self.logfile.write(f'succeed? True\n')
        self.logfile.write('instantReward: ' + str(instantReward) + '\n')
        self.logfile.write('EndTime: '+ str(endtime) + '\n')
        self.logfile.flush()
    
    def __del__(self):
        self.logfile.close()