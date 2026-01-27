import { useState, useEffect, useCallback } from 'react';
import type { Project, ProjectListApiResponse } from '../types/external';
import type { ProjectSelectorProps } from '../types/internal';
import { buildApiUrl } from '../utils/api_url_builder';
import { backendApiWrapper } from '../utils/api_client';
import { handleError } from '../utils/errorHandler';


export function ProjectSelector({ refreshKey, currentProjectUrl, onSelect, onError }: ProjectSelectorProps) {
    const [projects, setProjects] = useState<Project[]>([]);
    const [state, setState] = useState({
        isLoading: false,
        error: null as string | null,
    })

    const fetchProjects = useCallback((signal?: AbortSignal) => {
        setState({ isLoading: true, error: null });
        backendApiWrapper<undefined, ProjectListApiResponse>(
            'GET',
            buildApiUrl('/v1/projects'),
            undefined,
            signal
        )
            .then((resp) => {
                setProjects(resp.data || []);
                setState(prev => ({ ...prev, isLoading: false }));
            })
            .catch((error) => {
                // Suppress AbortError from being shown to the user
                if (error && error.name === 'AbortError') return;
                const message = error instanceof Error ? error.message : 'Failed to load projects';
                // show error to the user in this component
                setState(prev => ({ ...prev, error: message, isLoading: false }));
                // log/debug for developers
                handleError(message, { component: 'ProjectSelector' }, error);
                // notify the parent component so it can handle it at a higher level if needed
                onError?.(message);
            });
    }, [onError]);

    useEffect(() => {
        const controller = new AbortController();
        fetchProjects(controller.signal);
        return () => controller.abort(); // Cleanup: abort fetch on unmount or refreshKey change
    }, [refreshKey, fetchProjects]);

    if (state.isLoading) {
        return <div className="text-xs text-gray-500">Loading projects...</div>;
    }
    if (state.error) {
        return (
            <div className="text-xs text-red-500 flex items-center space-x-2">
                <span>{state.error}</span>
                <button type="button" className="underline text-blue-600" onClick={() => fetchProjects()}>Retry</button>
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