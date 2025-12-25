import ToolsList from "@/components/ToolsList";
import { Tool } from "@/types/tools";

const tools: Tool[] = [
  { id: '1', name: 'arXiv', description: 'Search and retrieve papers from arXiv' },
  { id: '2', name: 'Semantic Scholar', description: 'Literature search and citation analysis' },
  { id: '3', name: 'SymPy', description: 'Symbolic mathematics library' },
  { id: '4', name: 'SciPy', description: 'Scientific computing and statistics' }
];

export default function ToolsPage() {
  return (
    <div className="max-w-4xl mx-auto mt-8">
      <ToolsList tools={tools} />
    </div>
  );
}
