import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  IconButton,
  Paper,
  Grid,
  Rating,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { RootState, AppDispatch } from '../store';
import { fetchReviews, createReview, updateReview, deleteReview } from '../store/slices/performanceSlice';
import { fetchEmployees } from '../store/slices/employeesSlice';
import { PerformanceReview } from '../types';

interface ReviewFormData {
  id?: string;
  employee_id: string;
  reviewer_id: string;
  rating: number;
  comments: string;
  status: 'pending' | 'completed';
}

const initialFormData: ReviewFormData = {
  employee_id: '',
  reviewer_id: '',
  rating: 0,
  comments: '',
  status: 'pending',
};

export default function Performance() {
  const dispatch = useDispatch<AppDispatch>();
  const { data: reviews, loading, error } = useSelector((state: RootState) => state.performance);
  const { data: employees } = useSelector((state: RootState) => state.employees);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState<ReviewFormData>(initialFormData);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    dispatch(fetchReviews());
    dispatch(fetchEmployees());
  }, [dispatch]);

  const handleOpen = () => {
    setOpen(true);
    setIsEditing(false);
    setFormData(initialFormData);
  };

  const handleClose = () => {
    setOpen(false);
    setFormData(initialFormData);
  };

  const handleEdit = (review: PerformanceReview) => {
    setFormData({
      id: review.id,
      employee_id: review.employee_id,
      reviewer_id: review.reviewer_id,
      rating: review.rating,
      comments: review.comments,
      status: review.status as 'pending' | 'completed',
    });
    setIsEditing(true);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this review?')) {
      await dispatch(deleteReview(id));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isEditing && formData.id) {
      await dispatch(updateReview(formData as PerformanceReview));
    } else {
      const { id, ...newReview } = formData;
      await dispatch(createReview(newReview));
    }
    handleClose();
  };

  const columns: GridColDef[] = [
    {
      field: 'employee_id',
      headerName: 'Employee',
      width: 200,
      valueGetter: (params) => {
        const review = params.row as PerformanceReview;
        return review.employee?.name || 'Unknown';
      },
    },
    {
      field: 'reviewer_id',
      headerName: 'Reviewer',
      width: 200,
      valueGetter: (params) => {
        const review = params.row as PerformanceReview;
        return review.reviewer?.name || 'Unknown';
      },
    },
    {
      field: 'rating',
      headerName: 'Rating',
      width: 130,
      renderCell: (params) => <Rating value={params.value} readOnly />,
    },
    {
      field: 'created_at',
      headerName: 'Review Date',
      width: 130,
      valueFormatter: (params) => new Date(params.value).toLocaleDateString(),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 130,
      renderCell: (params) => (
        <Typography
          color={params.value === 'completed' ? 'success.main' : 'warning.main'}
        >
          {params.value}
        </Typography>
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      renderCell: (params) => (
        <Box>
          <IconButton
            size="small"
            onClick={() => handleEdit(params.row)}
            color="primary"
          >
            <EditIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => handleDelete(params.row.id)}
            color="error"
          >
            <DeleteIcon />
          </IconButton>
        </Box>
      ),
    },
  ];

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Performance Reviews</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpen}
        >
          Create Review
        </Button>
      </Box>

      {error && (
        <Typography color="error" mb={2}>
          {error}
        </Typography>
      )}

      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={reviews || []}
          columns={columns}
          initialState={{
            pagination: {
              paginationModel: { page: 0, pageSize: 10 },
            },
          }}
          pageSizeOptions={[10, 25, 50]}
          checkboxSelection
          disableRowSelectionOnClick
          loading={loading}
        />
      </Paper>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{isEditing ? 'Edit Review' : 'Create Review'}</DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <FormControl fullWidth required>
                  <InputLabel>Employee</InputLabel>
                  <Select
                    value={formData.employee_id}
                    onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                    label="Employee"
                  >
                    {employees?.map((employee) => (
                      <MenuItem key={employee.id} value={employee.id}>
                        {employee.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth required>
                  <InputLabel>Reviewer</InputLabel>
                  <Select
                    value={formData.reviewer_id}
                    onChange={(e) => setFormData({ ...formData, reviewer_id: e.target.value })}
                    label="Reviewer"
                  >
                    {employees?.map((employee) => (
                      <MenuItem key={employee.id} value={employee.id}>
                        {employee.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <Typography component="legend">Rating</Typography>
                <Rating
                  value={formData.rating}
                  onChange={(_, newValue) => {
                    setFormData({ ...formData, rating: newValue || 0 });
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Comments"
                  multiline
                  rows={4}
                  value={formData.comments}
                  onChange={(e) => setFormData({ ...formData, comments: e.target.value })}
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth required>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as 'pending' | 'completed' })}
                    label="Status"
                  >
                    <MenuItem value="pending">Pending</MenuItem>
                    <MenuItem value="completed">Completed</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button type="submit" variant="contained" color="primary">
              {isEditing ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
} 