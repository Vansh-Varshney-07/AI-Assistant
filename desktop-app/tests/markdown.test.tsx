import React from 'react';
import {render,screen} from '@testing-library/react';
import {expect,it} from 'vitest';
import {Markdown} from '../src/renderer/Markdown';

it('renders useful code and tables without active model content or remote images',()=>{
  const {container}=render(<Markdown text={'## Findings\n\n| Field | Value |\n| --- | --- |\n| Evidence | present |\n\n```python\nprint("safe")\n```\n\n<script>alert(1)</script>\n<svg onload="alert(1)"></svg>\n\n![tracking](https://example.com/pixel)\n\n[unsafe](javascript:alert(1)) [source](https://example.com/reference)'}/>);
  expect(screen.getByRole('heading',{name:'Findings'})).toBeTruthy();
  expect(screen.getByRole('table').textContent).toContain('Evidence');
  expect(screen.getByLabelText('Code block').textContent).toContain('print("safe")');
  expect(container.querySelector('script,svg,img,iframe,object,a[href]')).toBeNull();
  expect(screen.getByText('(https://example.com/reference)')).toBeTruthy();
  expect(container.textContent).not.toContain('javascript:');
});
