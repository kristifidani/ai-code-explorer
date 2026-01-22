import type { Project } from '../types/external';

interface ProjectSelectorProps {
    currentProjectUrl?: string;
    onSelect: (projectUrl: string) => void;
    projects: Project[];
    loading: boolean;
    error: string | null;
    onRefresh: () => void;
}

export function ProjectSelector({ currentProjectUrl, onSelect, projects, loading, error, onRefresh }: ProjectSelectorProps) {
    if (loading) {
        return <div className="text-xs text-gray-500">Loading projects...</div>;
    }
    if (error) {
        return (
            <div className="text-xs text-red-500 flex items-center space-x-2">
                <span>{error}</span>
                <button className="underline text-blue-600" onClick={onRefresh}>Retry</button>
            </div>
        );
    }
    if (!projects.length) {
        return <div className="text-xs text-gray-400">No projects uploaded yet</div>;
    }
    return (
        <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-600">Your Projects:</span>
            <select
                className="text-xs px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-400 bg-white"
                value={currentProjectUrl || ''}
                onChange={e => onSelect(e.target.value)}
            >
                <option value="">General Chat</option>
                {projects.map((p) => (
                    <option key={p.canonical_github_url} value={p.canonical_github_url}>
                        {p.repo_name}
                    </option>
                ))}
            </select>
        </div>
    );
}