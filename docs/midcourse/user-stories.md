# User Stories - Mid-Course Project

## Feature: Due dates and overdue filter

1. As a task owner, I want to add a due date to each task, so that I can track deadlines alongside status and priority.
   Acceptance criteria:
   - A task can include an optional due date in the create and edit modal.
   - The API accepts only valid date values and rejects malformed input.
   - The due date is visible on the task card and in the task form.

2. As a team member, I want overdue tasks to be clearly marked, so that I can spot urgent work quickly.
   Acceptance criteria:
   - A task is marked overdue when its due date is earlier than the current date and the task is not Done.
   - The overdue state is shown clearly on the task card.
   - The overdue indicator updates correctly after a task is edited or moved between statuses.

3. As a user, I want to filter the board to show only overdue tasks, so that I can focus on deadlines that need attention.
   Acceptance criteria:
   - The board includes an optional overdue filter toggle.
   - When the filter is enabled, only overdue tasks are shown.
   - Clearing the filter restores the full board view.

AI assumption corrected: Copilot silently defined "overdue" as due date earlier than today AND status not Done, and never specified a date format. Decided: ISO 8601 (YYYY-MM-DD), date-only comparison, no timezone handling.

## Feature: Tags / labels

1. As a task creator, I want to add tags to a task, so that I can group related work by topic or team.
   Acceptance criteria:
   - A task can include one or more tags in the create and edit modal.
   - Tags are trimmed and non-empty values are accepted.
   - Blank or whitespace-only tag values are rejected.

2. As a user, I want to see tags as chips on each task card, so that I can scan work quickly.
   Acceptance criteria:
   - Each valid tag is displayed as a chip on the task card.
   - Tags are visually distinct from the task title and metadata.
   - Tags remain visible after a task is edited.

3. As a user, I want to filter tasks by tag, so that I can focus on work from a specific area.
   Acceptance criteria:
   - The board includes a tag filter control.
   - Selecting a tag shows only tasks that include that tag.
   - Clearing the tag filter restores the full board view.

AI assumption corrected: Copilot proposed unlimited tags with no length cap, despite the brief calling out an optional max. Decided: maximum 5 tags per task, 30 characters each.