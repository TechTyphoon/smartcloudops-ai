"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { toast } from "sonner"
import { 
  Brain, 
  Plus, 
  Play, 
  MoreHorizontal,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw
} from "lucide-react"
import { useExperiments } from "@/lib/stores/mlops-store"
import { formatTimestamp, getStatusColor } from "@/lib/mlops-api"

export function ExperimentsPanel() {
  const { experiments, loading, error, fetch, create, optimisticCreate } = useExperiments()
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [creating, setCreating] = useState(false)

  // Form state for creating experiment
  const [newExperiment, setNewExperiment] = useState({
    name: "",
    description: "",
    tags: ""
  })

  useEffect(() => {
    fetch({ status: statusFilter === "all" ? undefined : statusFilter })
  }, [statusFilter, fetch])

  const handleCreateExperiment = async () => {
    try {
      if (!newExperiment.name.trim()) {
        toast.error('Experiment name is required')
        return
      }

      setCreating(true)

      const tags = newExperiment.tags
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)

      const experimentData = {
        name: newExperiment.name,
        description: newExperiment.description,
        tags
      }

      // Optimistic update - immediately show the experiment in the UI
      optimisticCreate(experimentData)
      setCreateDialogOpen(false)
      setNewExperiment({ name: "", description: "", tags: "" })
      
      toast.promise(
        create(experimentData),
        {
          loading: 'Creating experiment...',
          success: 'Experiment created successfully!',
          error: 'Failed to create experiment'
        }
      )

    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setCreating(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return <Play className="w-4 h-4" />
      case 'completed':
        return <CheckCircle className="w-4 h-4" />
      case 'failed':
        return <XCircle className="w-4 h-4" />
      default:
        return <Clock className="w-4 h-4" />
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading experiments...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-16 bg-muted rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header with Create Button and Filters */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h3 className="text-lg font-semibold">Experiments</h3>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Experiment
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Experiment</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={newExperiment.name}
                  onChange={(e) => setNewExperiment(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., anomaly-detection-v2"
                />
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={newExperiment.description}
                  onChange={(e) => setNewExperiment(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe the experiment goals and methodology..."
                />
              </div>
              <div>
                <Label htmlFor="tags">Tags (comma-separated)</Label>
                <Input
                  id="tags"
                  value={newExperiment.tags}
                  onChange={(e) => setNewExperiment(prev => ({ ...prev, tags: e.target.value }))}
                  placeholder="e.g., anomaly-detection, v2, production"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateExperiment}>
                  Create Experiment
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Experiments Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Runs</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Tags</TableHead>
                <TableHead className="w-12"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {experiments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <div className="flex flex-col items-center gap-2">
                      <Brain className="h-8 w-8 text-muted-foreground" />
                      <p className="text-sm text-muted-foreground">No experiments found</p>
                      <p className="text-xs text-muted-foreground">
                        Create your first experiment to get started
                      </p>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                experiments.map((experiment) => (
                  <TableRow key={experiment.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{experiment.name}</div>
                        <div className="text-sm text-muted-foreground">
                          {experiment.description.length > 50 
                            ? `${experiment.description.substring(0, 50)}...` 
                            : experiment.description
                          }
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={`${getStatusColor(experiment.status)}/10 text-${getStatusColor(experiment.status).replace('bg-', '')} border-${getStatusColor(experiment.status).replace('bg-', '')}/20`}
                      >
                        {getStatusIcon(experiment.status)}
                        <span className="ml-1">{experiment.status}</span>
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="font-medium">{experiment.run_count}</span>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatTimestamp(experiment.created_at)}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1 flex-wrap">
                        {experiment.tags.slice(0, 2).map((tag) => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {experiment.tags.length > 2 && (
                          <Badge variant="secondary" className="text-xs">
                            +{experiment.tags.length - 2}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="w-4 h-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
