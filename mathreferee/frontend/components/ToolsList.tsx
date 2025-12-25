import { Tool } from '../types/tools';
import { List, ListItem, ListItemText, Paper, Typography } from '@mui/material';

interface Props {
  tools: Tool[];
}

export default function ToolsList({ tools }: Props) {
  return (
    <Paper variant="outlined">
      <Typography variant="h6" sx={{ p: 2 }}>Available Tools</Typography>
      <List>
        {tools.map((tool) => (
          <ListItem key={tool.id} divider>
            <ListItemText primary={tool.name} secondary={tool.description} />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
}