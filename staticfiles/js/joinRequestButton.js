const JoinRequestButton = ({ projectId, initialStatus }) => {
    const [status, setStatus] = React.useState(initialStatus);
    const [isLoading, setIsLoading] = React.useState(false);

    const handleRequest = async () => {
        setIsLoading(true);
        try {
            const response = await fetch(`/project/${projectId}/request-join/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
            });
            if (response.ok) {
                setStatus('pending');
            }
        } catch (error) {
            console.error('Error:', error);
        }
        setIsLoading(false);
    };

    return React.createElement(
        'button',
        {
            onClick: handleRequest,
            disabled: status === 'pending' || isLoading,
            className: `join-btn ${status === 'pending' ? 'pending' : 'request'}`,
        },
        status === 'pending' ? 'Request Pending' : 'Request to Join'
    );
};