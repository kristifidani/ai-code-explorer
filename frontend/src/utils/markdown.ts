/**
 *  For formatting markdown content in AI responses displayed in the chat box.
*/

import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

// Configure markdown-it for better formatting
const md = new MarkdownIt({
    breaks: true,
    html: false,
    linkify: false,
    typographer: false,
})

// Custom renderer for consistent spacing
md.renderer.rules.paragraph_open = () => '<p class="chat-p">'
md.renderer.rules.paragraph_close = () => '</p>'
md.renderer.rules.bullet_list_open = () => '<ul class="chat-ul">'
md.renderer.rules.bullet_list_close = () => '</ul>'
md.renderer.rules.list_item_open = () => '<li class="chat-li">'
md.renderer.rules.list_item_close = () => '</li>'

/**
 * Renders markdown to sanitized HTML for safe DOM insertion.
 */
export const renderMarkdown = (content: string): string => {
    return DOMPurify.sanitize(md.render(content))
}