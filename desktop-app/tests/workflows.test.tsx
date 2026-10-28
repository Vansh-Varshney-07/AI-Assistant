import React from 'react';
import {render,screen,fireEvent,waitFor,act} from '@testing-library/react';
import {expect,it,vi} from 'vitest';
import {WorkflowBuilder} from '../src/renderer/Workflows';
function fixture(){const api={workflows:vi.fn(async()=>[]),startWorkflow:vi.fn(async()=>({id:'run',status:'completed',digest:'digest',definition:{title:'Test',version:1,nodes:[]},nodes:[],events:[],metrics:{worker_invocations:0}})),workflow:vi.fn(),cancelWorkflow:vi.fn(),selectFiles:vi.fn()} as any;const perform=async(job:any,then:any)=>{const result=await job();then?.(result);};return {api,perform};}
it('editing a finite workflow never starts it or grants access',async()=>{
 const {api,perform}=fixture();render(<WorkflowBuilder api={api} space="a" files={null} busy={false} act={perform} setFiles={vi.fn()}/>);
 await waitFor(()=>expect(api.workflows).toHaveBeenCalledWith('a'));
 fireEvent.click(screen.getByRole('button',{name:'Add step'}));fireEvent.change(screen.getByLabelText('Workflow title'),{target:{value:'Draft only'}});
 expect(api.startWorkflow).not.toHaveBeenCalled();expect(api.selectFiles).not.toHaveBeenCalled();expect((screen.getByRole('button',{name:'Review and start workflow'}) as HTMLButtonElement).disabled).toBe(true);
});
it('submits the explicit selected source and finite dependencies through review',async()=>{
 const {api,perform}=fixture();render(<WorkflowBuilder api={api} space="a" files={{files:[{id:'opaque',name:'selected.md'}]}} busy={false} act={perform} setFiles={vi.fn()}/>);
 fireEvent.click(screen.getByRole('button',{name:'Add step'}));fireEvent.click(screen.getByRole('button',{name:'Review and start workflow'}));
 await waitFor(()=>expect(api.startWorkflow).toHaveBeenCalledTimes(1));const [space,definition]=api.startWorkflow.mock.calls[0];expect(space).toBe('a');expect(definition.nodes[1].dependencies).toEqual(['step1']);expect(definition.nodes.every((n:any)=>n.reference==='opaque')).toBe(true);expect(definition.version).toBe(1);
 await screen.findByRole('heading',{name:'Test · completed'});
});
it('ignores a late history result from another space',async()=>{
 const {api,perform}=fixture();let finish!:(v:any)=>void;api.workflows.mockImplementationOnce(()=>new Promise(resolve=>{finish=resolve;}));
 const props={api,files:null,busy:false,act:perform,setFiles:vi.fn()};const view=render(<WorkflowBuilder {...props} space="a"/>);view.rerender(<WorkflowBuilder {...props} space="b"/>);
 await act(async()=>finish([{id:'private',status:'failed',definition:{title:'PRIVATE_A'}}]));expect(screen.queryByText('PRIVATE_A')).toBeNull();
});
