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
                if (error instanceof Error && error.name === 'AbortError') {
                    setState(prev => ({ ...prev, isLoading: false }));
                    return;
                }
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
        return (
            <div className="flex items-center justify-end w-full">
                <div className="bg-white/80 border border-gray-200 rounded-lg px-4 py-2 shadow-sm flex items-center gap-2 min-w-[220px]">
                    <span className="text-xs text-gray-500">Loading projects...</span>
                </div>
            </div>
        );
    }
    if (state.error) {
        return (
            <div className="flex items-center justify-end w-full">
                <div className="bg-white/80 border border-red-200 rounded-lg px-4 py-2 shadow-sm flex items-center gap-2 min-w-[220px]">
                    <span className="text-xs text-red-500 font-medium">{state.error}</span>
                    <button type="button" className="text-xs underline text-blue-600 hover:text-blue-800" onClick={() => fetchProjects()}>Retry</button>
                </div>
            </div>
        );
    }
    if (!projects.length) {
        return (
            <div className="flex items-center justify-end w-full">
                <div className="bg-white/80 border border-gray-200 rounded-lg px-4 py-2 shadow-sm flex items-center gap-2 min-w-[220px]">
                    <span className="text-xs text-gray-400">No projects uploaded yet</span>
                </div>
            </div>
        );
    }
    return (
        <div className="flex items-center justify-end w-full">
            <div className="bg-white/80 border border-gray-200 rounded-lg px-4 py-2 shadow-sm flex items-center gap-3 min-w-[220px]">
                <label htmlFor="project-selector" className="text-xs text-gray-700 font-semibold mr-1 whitespace-nowrap">Your Projects:</label>
                <div className="relative w-full">
                    <select
                        id="project-selector"
                        className="text-xs w-full pl-2 pr-7 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white appearance-none transition-colors duration-150"
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
                    {/* Custom dropdown arrow */}
                    <div className="pointer-events-none absolute inset-y-0 right-2 flex items-center">
                        <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                        </svg>
                    </div>
                </div>
            </div>
        </div>
    );
}