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
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { toast } from "sonner"
import { 
  Layers, 
  Plus, 
  MoreHorizontal,
  Upload,
  Download,
  Settings,
  TrendingUp,
  Shield,
  Archive,
  AlertTriangle
} from "lucide-react"
import { useModels } from "@/lib/stores/mlops-store"
import { formatTimestamp, getStatusColor, getStatusText } from "@/lib/mlops-api"

export function ModelsPanel() {
  const { models, loading, error, fetch, register, updateStatus, optimisticUpdateStatus } = useModels()
  const [registerDialogOpen, setRegisterDialogOpen] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [registering, setRegistering] = useState(false)

  // Form state for registering model
  const [newModel, setNewModel] = useState({
    name: "",
    version: "",
    model_path: "",
    framework: "",
    tags: "",
    description: ""
  })

  useEffect(() => {
    fetch({ status: statusFilter === "all" ? undefined : statusFilter })
  }, [statusFilter, fetch])

  const handleRegisterModel = async () => {
    try {
      if (!newModel.name.trim() || !newModel.version.trim() || !newModel.model_path.trim()) {
        toast.error('Name, version, and model path are required')
        return
      }

      setRegistering(true)

      const tags = newModel.tags
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)

      const modelData = {
        name: newModel.name,
        version: newModel.version,
        model_path: newModel.model_path,
        framework: newModel.framework || "unknown",
        tags,
        metadata: newModel.description ? { description: newModel.description } : {}
      }

      setRegisterDialogOpen(false)
      setNewModel({ name: "", version: "", model_path: "", framework: "", tags: "", description: "" })
      
      toast.promise(
        register(modelData),
        {
          loading: 'Registering model...',
          success: 'Model registered successfully!',
          error: 'Failed to register model'
        }
      )

    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setRegistering(false)
    }
  }

  const handleUpdateStatus = async (modelId: string, newStatus: string) => {
    try {
      // Optimistic update - immediately show the status change
      optimisticUpdateStatus(modelId, newStatus)
      
      toast.promise(
        updateStatus(modelId, newStatus),
        {
          loading: `Updating model status to ${newStatus}...`,
          success: 'Model status updated successfully!',
          error: 'Failed to update model status'
        }
      )

    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'production':
        return <Shield className="w-4 h-4" />
      case 'staging':
        return <Settings className="w-4 h-4" />
      case 'archived':
        return <Archive className="w-4 h-4" />
      default:
        return <Layers className="w-4 h-4" />
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading models...</CardTitle>
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
      {/* Header with Register Button and Filters */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h3 className="text-lg font-semibold">Model Registry</h3>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="production">Production</SelectItem>
              <SelectItem value="staging">Staging</SelectItem>
              <SelectItem value="archived">Archived</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <Dialog open={registerDialogOpen} onOpenChange={setRegisterDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Register Model
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Register New Model</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="model-name">Model Name</Label>
                <Input
                  id="model-name"
                  value={newModel.name}
                  onChange={(e) => setNewModel(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., anomaly-detector"
                />
              </div>
              <div>
                <Label htmlFor="model-version">Version</Label>
                <Input
                  id="model-version"
                  value={newModel.version}
                  onChange={(e) => setNewModel(prev => ({ ...prev, version: e.target.value }))}
                  placeholder="e.g., 1.0.0"
                />
              </div>
              <div>
                <Label htmlFor="model-path">Model Path</Label>
                <Input
                  id="model-path"
                  value={newModel.model_path}
                  onChange={(e) => setNewModel(prev => ({ ...prev, model_path: e.target.value }))}
                  placeholder="e.g., /models/anomaly_detector.pkl"
                />
              </div>
              <div>
                <Label htmlFor="framework">Framework</Label>
                <Select value={newModel.framework} onValueChange={(value) => setNewModel(prev => ({ ...prev, framework: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select framework" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="scikit-learn">Scikit-learn</SelectItem>
                    <SelectItem value="tensorflow">TensorFlow</SelectItem>
                    <SelectItem value="pytorch">PyTorch</SelectItem>
                    <SelectItem value="xgboost">XGBoost</SelectItem>
                    <SelectItem value="lightgbm">LightGBM</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="model-tags">Tags (comma-separated)</Label>
                <Input
                  id="model-tags"
                  value={newModel.tags}
                  onChange={(e) => setNewModel(prev => ({ ...prev, tags: e.target.value }))}
                  placeholder="e.g., anomaly-detection, production-ready"
                />
              </div>
              <div>
                <Label htmlFor="model-description">Description</Label>
                <Textarea
                  id="model-description"
                  value={newModel.description}
                  onChange={(e) => setNewModel(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe the model's purpose and capabilities..."
                  rows={3}
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setRegisterDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleRegisterModel}>
                  Register Model
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Models Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Model</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Framework</TableHead>
                <TableHead>Version</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Tags</TableHead>
                <TableHead className="w-12"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {models.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8">
                    <div className="flex flex-col items-center gap-2">
                      <Layers className="h-8 w-8 text-muted-foreground" />
                      <p className="text-sm text-muted-foreground">No models registered</p>
                      <p className="text-xs text-muted-foreground">
                        Register your first model to get started
                      </p>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                models.map((model) => (
                  <TableRow key={model.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{model.name}</div>
                        <div className="text-sm text-muted-foreground">
                          {model.metadata?.description && model.metadata.description.length > 50 
                            ? `${model.metadata.description.substring(0, 50)}...` 
                            : model.metadata?.description || "No description"
                          }
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={`${getStatusColor(model.status)}/10 border-${getStatusColor(model.status).replace('bg-', '')}/20`}
                      >
                        {getStatusIcon(model.status)}
                        <span className="ml-1">{getStatusText(model.status)}</span>
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary" className="text-xs">
                        {model.framework}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="font-mono text-sm">{model.version}</span>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatTimestamp(model.created_at)}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1 flex-wrap">
                        {model.tags.slice(0, 2).map((tag) => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {model.tags.length > 2 && (
                          <Badge variant="secondary" className="text-xs">
                            +{model.tags.length - 2}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem 
                            onClick={() => handleUpdateStatus(model.id, 'production')}
                            disabled={model.status === 'production'}
                          >
                            <Shield className="w-4 h-4 mr-2" />
                            Promote to Production
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={() => handleUpdateStatus(model.id, 'staging')}
                            disabled={model.status === 'staging'}
                          >
                            <Settings className="w-4 h-4 mr-2" />
                            Move to Staging
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={() => handleUpdateStatus(model.id, 'archived')}
                            disabled={model.status === 'archived'}
                          >
                            <Archive className="w-4 h-4 mr-2" />
                            Archive Model
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Download className="w-4 h-4 mr-2" />
                            Download Model
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <TrendingUp className="w-4 h-4 mr-2" />
                            View Metrics
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
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
